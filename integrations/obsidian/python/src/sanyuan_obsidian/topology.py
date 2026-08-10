from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

from .models import Candidate, InjectionItem, ReadProjection


class RoutingTable:
    def __init__(self, path: Path | None):
        self.path = path
        self.routes: dict[str, dict[str, Any]] = {}
        self.degradation: str | None = None
        if path:
            self._load(path)

    def _load(self, path: Path) -> None:
        if not path.exists():
            self.degradation = "routing-table-missing"
            return
        try:
            if path.suffix.lower() == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix.lower() in {".yaml", ".yml"}:
                try:
                    import yaml  # type: ignore[import-not-found]
                except ImportError:
                    self.degradation = "routing-table-yaml-parser-unavailable"
                    return
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            else:
                self.degradation = "routing-table-format-unsupported"
                return
        except (OSError, ValueError, json.JSONDecodeError):
            self.degradation = "routing-table-invalid"
            return
        routes = data.get("routes") if isinstance(data, dict) else None
        if not isinstance(routes, dict):
            self.degradation = "routing-table-has-no-routes"
            return
        self.routes = {
            str(key): value
            for key, value in routes.items()
            if isinstance(value, dict)
        }

    @staticmethod
    def key(query_axes: Sequence[str]) -> str:
        return "|".join(" ".join(axis.lower().split()) for axis in query_axes if axis.strip())

    def lookup(self, query_axes: Sequence[str] | None) -> dict[str, Any] | None:
        if not query_axes:
            return None
        return self.routes.get(self.key(query_axes))


def _excerpt(content: str, limit: int = 520) -> str:
    compact = " ".join(content.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _topology_level(candidate: Candidate) -> str:
    depth = len([part for part in candidate.path.replace("\\", "/").split("/") if part])
    if depth <= 1:
        return "top"
    if depth >= 4 or "#" in candidate.source_anchor:
        return "bottom"
    return "middle"


def project_candidate(
    query: str,
    candidate: Candidate,
    method: str,
    mode: str,
) -> ReadProjection:
    projection_id = "read_projection_" + hashlib.sha256(
        f"{query}\0{candidate.candidate_id}".encode("utf-8")
    ).hexdigest()[:16]
    mutual_refs = [
        str(value)
        for value in candidate.metadata.get("mutual_refs", [])
        if str(value).strip()
    ]
    store_refs = [
        str(value)
        for value in candidate.metadata.get("store_refs", [])
        if str(value).strip()
    ]
    read_refs = [
        str(value)
        for value in candidate.metadata.get("read_refs", [])
        if str(value).strip()
    ]
    boundaries = [
        "检索命中只表示词项或向量相关，不构成事实正确性、因果性或证据强度判断。"
    ]
    if not mutual_refs:
        boundaries.append(
            "候选未提供 MutualNode 引用，因此这里只生成临时 ReadProjection，不宣称完整 CouplingState。"
        )
    if not store_refs:
        boundaries.append(
            "Obsidian 行仅作为来源锚点；未提供正式 StoreNode ID，不能冒充来源藏节点。"
        )
    if mode == "minimal":
        original_form = candidate.title
        observed = "仅保留来源标题与路径。"
    else:
        original_form = _excerpt(candidate.content)
        observed = (
            f"FTS={candidate.fts_score:.3f}; vector={candidate.vector_score:.3f}; "
            f"lexical={candidate.lexical_score:.3f}"
        )
    return ReadProjection(
        projection_id=projection_id,
        source_store_ids=store_refs,
        source_read_ids=read_refs,
        source_anchors=[candidate.source_anchor],
        store_projection={
            "tiancai": {
                "patterns": candidate.metadata.get("patterns", []),
                "constraints": ["受当前索引快照、分块与检索配置约束。"],
                "timescale": candidate.metadata.get("updated_at", "unknown"),
            },
            "dicai": {
                "environment": "Obsidian vault index",
                "carrier": candidate.path,
                "boundary": candidate.source_anchor,
                "storage_condition": "只读检索；不修改 Markdown 源文件。",
            },
            "rencai": {
                "actors": candidate.metadata.get("actors", []),
                "practices": ["Markdown 记录", "SQLite FTS5 索引"],
                "recording_action": "该文本块被写入并进入可检索索引。",
            },
            "status": "transient-not-store-node",
        },
        tianti={
            "original_form": original_form,
            "observed_structure": observed,
            "unknowns": ["候选内容尚未经过任务级事实核验。"],
        },
        diti={
            "method": method,
            "tool": "sanyuan-obsidian sidecar",
            "path": candidate.path,
            "filter": "G1 union -> G2 discard -> G3 rerank",
            "scope": mode,
            "loss_risk": "分块、FTS 分词、向量压缩与 top_k 截断可能遗漏相关内容。",
        },
        renti={
            "reader": "retrieval pipeline",
            "reading_record": f"该候选被查询“{query}”召回并排序。",
            "interpretation": "候选可作为后续阅读上下文，不自动成为结论。",
            "hypothesis": "",
            "disagreement": "",
        },
        abstraction={
            "derived_pattern": "查询与候选之间存在可观测的检索信号。",
            "applicability": "仅适用于本次查询与当前索引快照。",
            "limitations": "未执行全文事实核验或因果判断。",
        },
        topology_level=_topology_level(candidate),
        mutual_refs=mutual_refs,
        coupling_status=(
            "observed" if mutual_refs and store_refs and read_refs else "incomplete"
        ),
        evidence_boundaries=boundaries,
    )


def format_injection(items: Sequence[InjectionItem], mode: str) -> str:
    if not items:
        return "read: none"
    blocks: list[str] = []
    for index, item in enumerate(items, start=1):
        candidate = item.candidate
        projection = item.projection
        if mode == "minimal":
            blocks.append(
                f"[[天题×地题×人题: {candidate.title}]]\n"
                f"来源锚点: [[{candidate.source_anchor}]]"
            )
            continue
        store_line = (
            "来源藏节点: " + " ".join(f"[[{ref}]]" for ref in projection.source_store_ids)
            if projection.source_store_ids
            else "来源藏节点: pending"
        )
        blocks.append(
            f"[[天题×地题×人题: {candidate.title}]]\n"
            f"归状态: {projection.abstraction['derived_pattern']}\n"
            f"拓扑层级: {projection.topology_level}\n"
            f"{store_line}\n"
            f"来源锚点: [[{candidate.source_anchor}]]\n"
            f"读取摘要: {projection.tianti['original_form']}\n"
            f"证据边界: {' '.join(projection.evidence_boundaries)}\n"
            f"检索序位: {index}; rerank={candidate.rerank_score:.3f}"
        )
    return "\n\n".join(blocks)
