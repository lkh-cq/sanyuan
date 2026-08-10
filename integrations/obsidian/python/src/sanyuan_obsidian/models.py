from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Candidate:
    candidate_id: str
    path: str
    title: str
    content: str
    source_anchor: str
    fts_score: float = 0.0
    vector_score: float = 0.0
    lexical_score: float = 0.0
    rerank_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReadProjection:
    projection_id: str
    source_store_ids: list[str]
    source_read_ids: list[str]
    source_anchors: list[str]
    store_projection: dict[str, Any]
    tianti: dict[str, Any]
    diti: dict[str, Any]
    renti: dict[str, Any]
    abstraction: dict[str, Any]
    topology_level: str
    mutual_refs: list[str] = field(default_factory=list)
    coupling_status: str = "incomplete"
    evidence_boundaries: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InjectionItem:
    candidate: Candidate
    projection: ReadProjection

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "projection": self.projection.to_dict(),
        }


@dataclass(slots=True)
class InjectionResult:
    query: str
    triggered: bool
    mode: str
    injection: str
    items: list[InjectionItem] = field(default_factory=list)
    routing: dict[str, Any] | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "triggered": self.triggered,
            "mode": self.mode,
            "injection": self.injection,
            "items": [item.to_dict() for item in self.items],
            "routing": self.routing,
            "diagnostics": self.diagnostics,
        }
