#!/usr/bin/env python3
"""Deterministic guardrails for the V3.4 RAG-front-end migration.

This validator checks contracts and obvious permission regressions. It does not
claim semantic correctness, RAG quality, or user-intent understanding.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"


def fail(msg: str, failures: list[str]) -> None:
    failures.append(msg)


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []

    required = [
        REF / "rag-frontend-governance.md",
        REF / "filter-ratchet-permission.md",
        REF / "update-plan-rag-frontend-v3.4.md",
        REF / "fast-view-recipe.yaml",
        REF / "schema-filter-lease.schema.json",
        REF / "schema-rag-request-frame.schema.json",
    ]
    for path in required:
        if not path.exists():
            fail(f"missing V3.4 front-end artifact: {path.relative_to(ROOT)}", failures)

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for marker in (
        "RAG 前端",
        "FilterLease=CLOSED",
        "Normalization is lossless alignment",
        "rho/theta are advisory only",
    ):
        if marker not in skill:
            fail(f"SKILL.md missing guardrail marker: {marker}", failures)

    active_docs = {
        "task-boundary.md": (REF / "task-boundary.md").read_text(encoding="utf-8"),
        "meta-normalization.md": (REF / "meta-normalization.md").read_text(encoding="utf-8"),
        "hu-normalization.md": (REF / "hu-normalization.md").read_text(encoding="utf-8"),
        "research-recipe.yaml": (REF / "research-recipe.yaml").read_text(encoding="utf-8"),
        "fast-view-recipe.yaml": (REF / "fast-view-recipe.yaml").read_text(encoding="utf-8"),
    }
    forbidden_fragments = (
        "indifferent: 任务无关, 可删除",
        "indifferent: 任务无关的关系, 可删除",
        "任务条件压缩",
        "epsilon_T: 0.2",
    )
    for name, text in active_docs.items():
        for fragment in forbidden_fragments:
            if fragment in text:
                fail(f"{name} contains legacy lossy behavior: {fragment}", failures)

    task_schema = load_yaml(REF / "schema-task-boundary.schema.yaml")
    task_props = task_schema.get("properties", {})
    if "epsilon_T" in task_props:
        fail("TaskBoundary schema must not expose epsilon_T as a loss permission", failures)
    if "filter_permission" in task_props:
        fail("TaskBoundary schema must not contain filter_permission", failures)
    if task_props.get("output_target", {}).get("enum") != ["rag_request_frame"]:
        fail("TaskBoundary output_target must be rag_request_frame only", failures)

    for schema_name in (
        "schema-meta-normalization.schema.yaml",
        "schema-hu-normalization.schema.yaml",
    ):
        schema = load_yaml(REF / schema_name)
        props = schema.get("properties", {})
        for legacy in ("omitted_features", "recovery_refs", "loss"):
            if legacy in props:
                fail(f"{schema_name} still exposes default lossy field: {legacy}", failures)

    lease = load_json(REF / "schema-filter-lease.schema.json")
    lprops = lease.get("properties", {})
    issued = lprops.get("issued_by", {}).get("enum")
    if issued != ["user_explicit"]:
        fail("FilterLease issued_by must be user_explicit only", failures)
    if lprops.get("inheritable", {}).get("const") is not False:
        fail("FilterLease inheritable must be false", failures)
    if lprops.get("refreshable", {}).get("const") is not False:
        fail("FilterLease refreshable must be false", failures)
    if lprops.get("source_mutation_allowed", {}).get("const") is not False:
        fail("FilterLease source_mutation_allowed must be false", failures)

    batch = load_yaml(REF / "fast-filter-recipe.yaml")
    gate = batch.get("entry_gate", {}).get("require_all", [])
    gate_text = json.dumps(gate, ensure_ascii=False, sort_keys=True)
    for marker in (
        "user_explicit_authorization",
        "filter_lease_state",
        "large_batch",
        "high",
        "filter_spec_frozen",
    ):
        if marker not in gate_text:
            fail(f"batch-filter entry gate missing: {marker}", failures)

    research = load_yaml(REF / "research-recipe.yaml")
    research_text = json.dumps(research, ensure_ascii=False)
    if "RAGRequestFrame" not in research_text:
        fail("research recipe must terminate in RAGRequestFrame", failures)
    if "reader-facing-analysis" in research_text:
        fail("reader-facing-analysis must not remain in the front-end core recipe", failures)

    rho = (REF / "rho-convergence.md").read_text(encoding="utf-8")
    theta = (REF / "theta-switching.md").read_text(encoding="utf-8")
    if "advisory" not in rho.lower() or "FilterLease" not in rho:
        fail("rho module must declare advisory-only and FilterLease isolation", failures)
    if "advisory" not in theta.lower() or "FilterLease" not in theta:
        fail("theta module must declare advisory-only and FilterLease isolation", failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        print(f"{len(failures)} front-end guardrail failure(s)")
        return 1

    print("PASS: V3.4 RAG-front-end guardrails are structurally enforced")
    print("NOTE: semantic fidelity and downstream RAG quality require forward tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
