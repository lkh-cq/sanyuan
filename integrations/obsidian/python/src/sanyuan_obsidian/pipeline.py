from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

from .config import EmbeddingConfig, PipelineConfig
from .models import Candidate, InjectionItem, InjectionResult
from .providers import (
    DoubaoEmbedder,
    EmbeddingProvider,
    NullEmbedder,
    SQLiteKnowledgeStore,
    cosine_similarity,
    rerank_candidates,
    should_retrieve,
)
from .topology import RoutingTable, format_injection, project_candidate


class ContextPipeline:
    def __init__(
        self,
        config: PipelineConfig | None = None,
        *,
        store: SQLiteKnowledgeStore | None = None,
        embedder: EmbeddingProvider | None = None,
    ):
        self.config = config or PipelineConfig.from_env()
        self.store = store or SQLiteKnowledgeStore(self.config)
        if embedder is not None:
            self.embedder = embedder
        else:
            embedding_config = EmbeddingConfig.from_env()
            self.embedder = (
                DoubaoEmbedder(embedding_config)
                if embedding_config.enabled
                else NullEmbedder()
            )
        self.routing = RoutingTable(self.config.routing_table_path)

    @staticmethod
    def _merge_candidates(groups: Sequence[Sequence[Candidate]]) -> list[Candidate]:
        merged: dict[str, Candidate] = {}
        for group in groups:
            for candidate in group:
                key = candidate.candidate_id
                existing = merged.get(key)
                if existing is None:
                    merged[key] = candidate
                    continue
                existing.fts_score = max(existing.fts_score, candidate.fts_score)
                existing.vector_score = max(existing.vector_score, candidate.vector_score)
                existing.metadata.update(candidate.metadata)
                if len(candidate.content) > len(existing.content):
                    existing.content = candidate.content
        return list(merged.values())

    def _embed_fts_candidates(
        self,
        query_vector: Sequence[float],
        candidates: Sequence[Candidate],
    ) -> None:
        if not candidates:
            return
        vectors = self.embedder.embed(
            [candidate.content[:6000] for candidate in candidates]
        )
        for candidate, vector in zip(candidates, vectors):
            candidate.vector_score = cosine_similarity(query_vector, vector)

    def retrieve_and_inject(
        self,
        query: str,
        top_k: int = 8,
        mode: str = "full",
        *,
        trigger_policy: str = "always",
        query_axes: list[str] | None = None,
        current_path: str | None = None,
    ) -> InjectionResult:
        started = time.perf_counter()
        normalized_query = " ".join(query.strip().split())
        if not normalized_query:
            raise ValueError("query must not be empty")
        if len(normalized_query) > self.config.max_query_chars:
            raise ValueError("query exceeds the configured character limit")
        if mode not in {"full", "fast", "minimal"}:
            raise ValueError("mode must be full, fast, or minimal")
        if trigger_policy not in {"always", "auto", "never"}:
            raise ValueError("trigger_policy must be always, auto, or never")
        if not 1 <= int(top_k) <= 32:
            raise ValueError("top_k must be between 1 and 32")

        intent, intent_reason = should_retrieve(normalized_query)
        triggered = trigger_policy == "always" or (
            trigger_policy == "auto" and intent
        )
        if trigger_policy == "never":
            triggered = False
        diagnostics: dict[str, Any] = {
            "trigger": {"policy": trigger_policy, "reason": intent_reason},
            "embedding_provider": self.embedder.name,
            "reranker": "transparent-hybrid-heuristic",
            "degraded": [],
            "stage_counts": {},
        }
        if not triggered:
            diagnostics["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 3)
            return InjectionResult(
                query=normalized_query,
                triggered=False,
                mode=mode,
                injection="read: skipped",
                diagnostics=diagnostics,
            )

        coarse_limit = max(int(top_k) * self.config.coarse_multiplier, int(top_k))
        fts_candidates = self.store.search_fts(normalized_query, coarse_limit)
        if not fts_candidates:
            diagnostics["degraded"].append("fts-unavailable-or-no-match")

        query_vector: list[float] | None = None
        vector_candidates: list[Candidate] = []
        if mode != "minimal" and self.embedder.enabled:
            try:
                query_vector = self.embedder.embed([normalized_query])[0]
                if self.store.vector_index_exists():
                    vector_candidates = self.store.search_vectors(
                        query_vector, coarse_limit
                    )
                elif fts_candidates:
                    self._embed_fts_candidates(query_vector, fts_candidates)
                    diagnostics["degraded"].append(
                        "vector-index-missing-candidate-rerank-only"
                    )
            except RuntimeError as exc:
                diagnostics["degraded"].append(f"embedding-failed:{exc}")
        elif mode != "minimal":
            diagnostics["degraded"].append("embedding-not-configured")

        merged = self._merge_candidates((fts_candidates, vector_candidates))
        ranked, stage_counts = rerank_candidates(
            normalized_query,
            merged,
            int(top_k),
            mode,
            current_path=current_path,
        )
        diagnostics["stage_counts"] = stage_counts
        method_parts = ["SQLite FTS5"]
        if query_vector is not None:
            method_parts.append("embedding cosine")
        method_parts.append("transparent heuristic rerank")
        method = " + ".join(method_parts)
        items = [
            InjectionItem(
                candidate=candidate,
                projection=project_candidate(
                    normalized_query, candidate, method=method, mode=mode
                ),
            )
            for candidate in ranked
        ]

        routing: dict[str, Any] | None = None
        if mode == "full":
            routing = self.routing.lookup(query_axes)
            if routing is None:
                if self.routing.degradation:
                    diagnostics["degraded"].append(self.routing.degradation)
                elif not query_axes:
                    diagnostics["degraded"].append("query-axes-not-supplied")
                else:
                    diagnostics["degraded"].append("routing-key-not-found")

        diagnostics["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 3)
        return InjectionResult(
            query=normalized_query,
            triggered=True,
            mode=mode,
            injection=format_injection(items, mode),
            items=items,
            routing=routing,
            diagnostics=diagnostics,
        )

    def health(self) -> dict[str, Any]:
        store = self.store.inspect()
        return {
            "status": "ok" if store["database_exists"] else "degraded",
            "store": store,
            "embedding_provider": self.embedder.name,
            "embedding_enabled": self.embedder.enabled,
            "routing_loaded": bool(self.routing.routes),
            "routing_degradation": self.routing.degradation,
        }


_DEFAULT_PIPELINE: ContextPipeline | None = None


def retrieve_and_inject(
    query: str,
    top_k: int = 8,
    mode: str = "full",
    *,
    trigger_policy: str = "always",
    query_axes: list[str] | None = None,
    current_path: str | None = None,
) -> InjectionResult:
    global _DEFAULT_PIPELINE
    if _DEFAULT_PIPELINE is None:
        _DEFAULT_PIPELINE = ContextPipeline()
    return _DEFAULT_PIPELINE.retrieve_and_inject(
        query,
        top_k=top_k,
        mode=mode,
        trigger_policy=trigger_policy,
        query_axes=query_axes,
        current_path=current_path,
    )
