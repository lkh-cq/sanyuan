from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import urllib.error
import urllib.request
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from .config import EmbeddingConfig, PipelineConfig
from .models import Candidate


class EmbeddingProvider(Protocol):
    name: str

    @property
    def enabled(self) -> bool: ...

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class NullEmbedder:
    name = "disabled"
    enabled = False

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        raise RuntimeError("embedding provider is not configured")


class DoubaoEmbedder:
    """Minimal OpenAI-compatible embeddings client for Doubao/Ark endpoints."""

    name = "doubao-openai-compatible"

    def __init__(self, config: EmbeddingConfig):
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.enabled

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not self.enabled:
            raise RuntimeError("embedding provider is not configured")
        if not texts:
            return []
        payload = json.dumps(
            {"model": self.config.model, "input": list(texts)},
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            self.config.base_url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "sanyuan-obsidian/0.1",
            },
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.config.timeout_seconds
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"embedding endpoint returned HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError("embedding endpoint request failed") from exc

        data = body.get("data")
        if not isinstance(data, list):
            raise RuntimeError("embedding endpoint response has no data array")
        ordered = sorted(data, key=lambda item: int(item.get("index", 0)))
        vectors = [item.get("embedding") for item in ordered]
        if len(vectors) != len(texts) or not all(isinstance(v, list) for v in vectors):
            raise RuntimeError("embedding endpoint returned an unexpected vector count")
        return [[float(value) for value in vector] for vector in vectors]


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


@dataclass(frozen=True, slots=True)
class FtsLayout:
    table: str
    columns: tuple[str, ...]
    path_column: str | None
    title_column: str | None
    content_column: str


class SQLiteKnowledgeStore:
    VECTOR_TABLE = "sanyuan_vector_index"

    def __init__(self, config: PipelineConfig):
        self.config = config
        self._layout: FtsLayout | None = None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.config.database_path,
            timeout=5.0,
            uri=False,
        )
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _quote(identifier: str) -> str:
        return '"' + identifier.replace('"', '""') + '"'

    def discover_fts(self, refresh: bool = False) -> FtsLayout | None:
        if self._layout is not None and not refresh:
            return self._layout
        if not self.config.database_path.exists():
            return None
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name, sql FROM sqlite_master "
                "WHERE type = 'table' AND lower(coalesce(sql, '')) LIKE '%using fts5%'"
            ).fetchall()
            names = [str(row["name"]) for row in rows]
            requested = self.config.fts_table
            if requested:
                if requested not in names:
                    raise RuntimeError(
                        f"configured FTS table {requested!r} was not found"
                    )
                table = requested
            elif names:
                preferred = [
                    name
                    for name in names
                    if any(token in name.lower() for token in ("note", "memory", "chunk"))
                ]
                table = (preferred or names)[0]
            else:
                return None

            columns = tuple(
                str(row["name"])
                for row in connection.execute(
                    f"PRAGMA table_info({self._quote(table)})"
                ).fetchall()
            )

        def choose(explicit: str | None, hints: tuple[str, ...]) -> str | None:
            if explicit:
                if explicit not in columns:
                    raise RuntimeError(
                        f"configured column {explicit!r} was not found in {table!r}"
                    )
                return explicit
            lowered = {column.lower(): column for column in columns}
            for hint in hints:
                if hint in lowered:
                    return lowered[hint]
            for column in columns:
                if any(hint in column.lower() for hint in hints):
                    return column
            return None

        content = choose(
            self.config.fts_content_column,
            ("content", "body", "text", "markdown", "chunk"),
        )
        if content is None:
            content = columns[-1] if columns else None
        if content is None:
            return None
        self._layout = FtsLayout(
            table=table,
            columns=columns,
            path_column=choose(
                self.config.fts_path_column, ("path", "file", "source", "uri")
            ),
            title_column=choose(
                self.config.fts_title_column, ("title", "name", "heading")
            ),
            content_column=content,
        )
        return self._layout

    @staticmethod
    def _fts_query(query: str) -> str:
        tokens = re.findall(r"[\w\u3400-\u9fff]+", query, flags=re.UNICODE)
        tokens = [token for token in tokens if token.strip()][:24]
        if not tokens:
            return '"' + query.replace('"', '""') + '"'
        return " OR ".join('"' + token.replace('"', '""') + '"' for token in tokens)

    def search_fts(self, query: str, limit: int) -> list[Candidate]:
        layout = self.discover_fts()
        if layout is None:
            return []
        table = self._quote(layout.table)
        content = self._quote(layout.content_column)
        path_expr = (
            self._quote(layout.path_column) if layout.path_column else "CAST(rowid AS TEXT)"
        )
        title_expr = (
            self._quote(layout.title_column) if layout.title_column else path_expr
        )
        sql = (
            f"SELECT rowid AS _rowid, {path_expr} AS _path, {title_expr} AS _title, "
            f"{content} AS _content, bm25({table}) AS _bm25 FROM {table} "
            f"WHERE {table} MATCH ? ORDER BY _bm25 LIMIT ?"
        )
        with self._connect() as connection:
            rows = connection.execute(sql, (self._fts_query(query), limit)).fetchall()
        candidates: list[Candidate] = []
        for rank, row in enumerate(rows):
            path = str(row["_path"] or row["_rowid"])
            title = str(row["_title"] or path)
            content_value = str(row["_content"] or "")
            candidate_id = hashlib.sha256(
                f"{layout.table}:{row['_rowid']}:{path}".encode("utf-8")
            ).hexdigest()[:20]
            candidates.append(
                Candidate(
                    candidate_id=candidate_id,
                    path=path,
                    title=title,
                    content=content_value,
                    source_anchor=f"obsidian:{path}#row={row['_rowid']}",
                    fts_score=1.0 / (rank + 1),
                    metadata={
                        "fts_table": layout.table,
                        "fts_rowid": row["_rowid"],
                        "bm25": float(row["_bm25"]),
                    },
                )
            )
        return candidates

    def vector_index_exists(self) -> bool:
        if not self.config.database_path.exists():
            return False
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                (self.VECTOR_TABLE,),
            ).fetchone()
        return row is not None

    def ensure_vector_index(self) -> None:
        with self._connect() as connection:
            connection.execute(
                f"CREATE TABLE IF NOT EXISTS {self.VECTOR_TABLE} ("
                "candidate_id TEXT PRIMARY KEY, path TEXT NOT NULL, title TEXT NOT NULL, "
                "content TEXT NOT NULL, source_anchor TEXT NOT NULL, "
                "embedding_json TEXT NOT NULL, content_hash TEXT NOT NULL, "
                "updated_at TEXT NOT NULL)"
            )

    def upsert_vector(self, candidate: Candidate, embedding: Sequence[float]) -> None:
        self.ensure_vector_index()
        digest = hashlib.sha256(candidate.content.encode("utf-8")).hexdigest()
        with self._connect() as connection:
            connection.execute(
                f"INSERT INTO {self.VECTOR_TABLE} "
                "(candidate_id, path, title, content, source_anchor, embedding_json, "
                "content_hash, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(candidate_id) DO UPDATE SET path=excluded.path, "
                "title=excluded.title, content=excluded.content, "
                "source_anchor=excluded.source_anchor, "
                "embedding_json=excluded.embedding_json, "
                "content_hash=excluded.content_hash, updated_at=excluded.updated_at",
                (
                    candidate.candidate_id,
                    candidate.path,
                    candidate.title,
                    candidate.content,
                    candidate.source_anchor,
                    json.dumps(list(embedding)),
                    digest,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def search_vectors(
        self, query_vector: Sequence[float], limit: int
    ) -> list[Candidate]:
        if not self.vector_index_exists():
            return []
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT candidate_id, path, title, content, source_anchor, "
                f"embedding_json FROM {self.VECTOR_TABLE}"
            ).fetchall()
        scored: list[tuple[float, sqlite3.Row]] = []
        for row in rows:
            try:
                vector = [float(value) for value in json.loads(row["embedding_json"])]
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            scored.append((cosine_similarity(query_vector, vector), row))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            Candidate(
                candidate_id=str(row["candidate_id"]),
                path=str(row["path"]),
                title=str(row["title"]),
                content=str(row["content"]),
                source_anchor=str(row["source_anchor"]),
                vector_score=float(score),
                metadata={"vector_index": self.VECTOR_TABLE},
            )
            for score, row in scored[:limit]
        ]

    def iter_fts(self, limit: int | None = None) -> Iterable[Candidate]:
        layout = self.discover_fts()
        if layout is None:
            return []
        table = self._quote(layout.table)
        content = self._quote(layout.content_column)
        path_expr = (
            self._quote(layout.path_column) if layout.path_column else "CAST(rowid AS TEXT)"
        )
        title_expr = (
            self._quote(layout.title_column) if layout.title_column else path_expr
        )
        sql = (
            f"SELECT rowid AS _rowid, {path_expr} AS _path, {title_expr} AS _title, "
            f"{content} AS _content FROM {table} ORDER BY rowid"
        )
        params: tuple[int, ...] = ()
        if limit is not None:
            sql += " LIMIT ?"
            params = (limit,)
        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [
            Candidate(
                candidate_id=hashlib.sha256(
                    f"{layout.table}:{row['_rowid']}:{row['_path']}".encode("utf-8")
                ).hexdigest()[:20],
                path=str(row["_path"] or row["_rowid"]),
                title=str(row["_title"] or row["_path"] or row["_rowid"]),
                content=str(row["_content"] or ""),
                source_anchor=f"obsidian:{row['_path']}#row={row['_rowid']}",
                metadata={"fts_table": layout.table, "fts_rowid": row["_rowid"]},
            )
            for row in rows
        ]

    def inspect(self) -> dict[str, object]:
        layout = self.discover_fts()
        return {
            "database_exists": self.config.database_path.exists(),
            "database_path": str(self.config.database_path),
            "fts": (
                {
                    "table": layout.table,
                    "columns": list(layout.columns),
                    "path_column": layout.path_column,
                    "title_column": layout.title_column,
                    "content_column": layout.content_column,
                }
                if layout
                else None
            ),
            "vector_index": self.vector_index_exists(),
        }


_INTENT_PATTERNS = (
    r"(?:查找|搜索|检索|找出|回忆|召回|翻出|定位).{0,16}(?:笔记|记录|资料|文献|上下文|内容)?",
    r"(?:之前|过去|我的|库里|笔记里).{0,12}(?:写过|提过|记录|内容|资料)",
    r"\b(?:find|search|retrieve|recall|look up|vault|my notes|context)\b",
)


def should_retrieve(query: str) -> tuple[bool, str]:
    normalized = " ".join(query.strip().split())
    if not normalized:
        return False, "empty-query"
    for pattern in _INTENT_PATTERNS:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            return True, "retrieval-intent-pattern"
    return False, "no-explicit-retrieval-intent"


def semantic_tokens(text: str) -> set[str]:
    lowered = text.lower()
    words = set(re.findall(r"[a-z0-9_]+", lowered))
    cjk_runs = re.findall(r"[\u3400-\u9fff]+", lowered)
    for run in cjk_runs:
        if len(run) == 1:
            words.add(run)
        else:
            words.update(run[index : index + 2] for index in range(len(run) - 1))
    return words


def rerank_candidates(
    query: str,
    candidates: Sequence[Candidate],
    top_k: int,
    mode: str,
    current_path: str | None = None,
) -> tuple[list[Candidate], dict[str, int]]:
    """Strict retrieval cascade; scores are not rho/theta or evidence strength."""

    stage_counts = {"g1_union": len(candidates)}
    query_tokens = semantic_tokens(query)
    survivors: dict[str, Candidate] = {}
    for candidate in candidates:
        content = candidate.content.strip()
        if not content:
            continue
        dedupe_key = hashlib.sha256(
            f"{candidate.path}\0{content}".encode("utf-8")
        ).hexdigest()
        existing = survivors.get(dedupe_key)
        if existing is None or (
            candidate.fts_score + candidate.vector_score
            > existing.fts_score + existing.vector_score
        ):
            survivors[dedupe_key] = candidate
    gated = list(survivors.values())
    stage_counts["g2_survivors"] = len(gated)

    for candidate in gated:
        candidate_tokens = semantic_tokens(candidate.title + "\n" + candidate.content[:6000])
        overlap = len(query_tokens & candidate_tokens) / max(1, len(query_tokens))
        candidate.lexical_score = overlap
        if mode == "minimal":
            score = 0.8 * candidate.fts_score + 0.2 * overlap
        else:
            vector = max(0.0, candidate.vector_score)
            score = 0.4 * candidate.fts_score + 0.4 * vector + 0.2 * overlap
        if current_path and candidate.path == current_path:
            score += 0.03
        candidate.rerank_score = score
    gated.sort(
        key=lambda candidate: (
            candidate.rerank_score,
            candidate.vector_score,
            candidate.fts_score,
        ),
        reverse=True,
    )
    ranked = gated[:top_k]
    stage_counts["g3_top_k"] = len(ranked)
    return ranked, stage_counts
