from __future__ import annotations

import json
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from sanyuan_obsidian.config import PipelineConfig
from sanyuan_obsidian.pipeline import ContextPipeline
from sanyuan_obsidian.providers import SQLiteKnowledgeStore
from sanyuan_obsidian.server import SidecarServer


class FakeEmbedder:
    name = "fake-test-embedder"
    enabled = True

    def embed(self, texts):
        vectors = []
        for text in texts:
            lowered = text.lower()
            vectors.append(
                [
                    1.0 if "pnpla8" in lowered else 0.0,
                    1.0 if "fibroblast" in lowered or "成纤维" in text else 0.0,
                    1.0,
                ]
            )
        return vectors


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.database = root / "obsidian-memory.db"
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "CREATE VIRTUAL TABLE notes_fts USING fts5(path, title, content)"
            )
            connection.executemany(
                "INSERT INTO notes_fts(path, title, content) VALUES (?, ?, ?)",
                [
                    (
                        "projects/periodontitis.md",
                        "PNPLA8 in fibroblasts",
                        "PNPLA8 is recorded as elevated in gingival fibroblast DEG results.",
                    ),
                    (
                        "methods/culture.md",
                        "Cell culture",
                        "Primary gingival fibroblast culture and passage notes.",
                    ),
                ],
            )
        self.config = PipelineConfig(database_path=self.database)

    def tearDown(self):
        self.temporary.cleanup()

    def test_retrieval_emits_current_read_injection_contract(self):
        pipeline = ContextPipeline(self.config, embedder=FakeEmbedder())
        result = pipeline.retrieve_and_inject("查找 PNPLA8 笔记", top_k=2)
        self.assertTrue(result.triggered)
        self.assertIn("[[天题×地题×人题:", result.injection)
        self.assertNotIn("天题×人题→地题", result.injection)
        self.assertGreaterEqual(len(result.items), 1)
        self.assertEqual(result.items[0].projection.coupling_status, "incomplete")
        self.assertIn(
            "vector-index-missing-candidate-rerank-only",
            result.diagnostics["degraded"],
        )

    def test_auto_trigger_is_conservative(self):
        pipeline = ContextPipeline(self.config, embedder=FakeEmbedder())
        skipped = pipeline.retrieve_and_inject(
            "PNPLA8", trigger_policy="auto", mode="minimal"
        )
        self.assertFalse(skipped.triggered)
        triggered = pipeline.retrieve_and_inject(
            "搜索我的 PNPLA8 笔记", trigger_policy="auto", mode="minimal"
        )
        self.assertTrue(triggered.triggered)

    def test_optional_route_lookup_is_exact_and_offline(self):
        routing = Path(self.temporary.name) / "routing.json"
        routing.write_text(
            json.dumps(
                {
                    "routes": {
                        "periodontitis|pnpla8|fibroblast": {
                            "n_position": "bn:test"
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        config = PipelineConfig(
            database_path=self.database, routing_table_path=routing
        )
        pipeline = ContextPipeline(config, embedder=FakeEmbedder())
        result = pipeline.retrieve_and_inject(
            "查找 PNPLA8 笔记",
            query_axes=["periodontitis", "PNPLA8", "fibroblast"],
        )
        self.assertEqual(result.routing, {"n_position": "bn:test"})

    def test_store_discovers_fts_layout(self):
        store = SQLiteKnowledgeStore(self.config)
        inspection = store.inspect()
        self.assertEqual(inspection["fts"]["table"], "notes_fts")
        self.assertEqual(inspection["fts"]["content_column"], "content")

    def test_rest_sidecar_requires_configured_token_and_returns_contract(self):
        pipeline = ContextPipeline(self.config, embedder=FakeEmbedder())
        server = SidecarServer(("127.0.0.1", 0), pipeline, token="test-token")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        try:
            with self.assertRaises(urllib.error.HTTPError) as unauthorized:
                urllib.request.urlopen(f"http://{host}:{port}/health", timeout=2)
            self.assertEqual(unauthorized.exception.code, 401)

            payload = json.dumps(
                {
                    "query": "搜索我的 PNPLA8 笔记",
                    "top_k": 1,
                    "mode": "full",
                    "trigger_policy": "auto",
                }
            ).encode("utf-8")
            request = urllib.request.Request(
                f"http://{host}:{port}/v1/retrieve-and-inject",
                data=payload,
                method="POST",
                headers={
                    "Authorization": "Bearer test-token",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(request, timeout=2) as response:
                body = json.loads(response.read().decode("utf-8"))
            self.assertTrue(body["triggered"])
            self.assertIn("[[天题×地题×人题:", body["injection"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
