#!/usr/bin/env python3
"""Validate systematic-retrieval branch protocol and retrieval plans.

规则 (见 references/systematic-retrieval.md 与 references/retrieval-protocol.yaml):
- 协议结构: 三阶段 (expansion/audit/convergence) 各含 name/goal/strategy/actions/acceptance
- 循环: 六步 (formulate/execute/ingest/audit/revise_keywords/decide),
  max_rounds_default <= max_rounds_hard <= 5, 停止条件非空
- 盲点: 恰好七类, 每类含 description/detection/response
- 来源: 恰好四类, 每类含 name/examples/conventions/evidence_grade/notes
- 关键词变更动作: broaden/narrow/swap_axis/swap_vocabulary/swap_language/swap_source_class + rule
- 鲁棒性: channel_failure(含 rule/retry)/dedup/source_grading/degradation/traceability
- 产物: plan/round/followup 各含 name/path_pattern/required_fields
- 计划模式 (--plan): 按 schema-retrieval-plan.schema.yaml 校验必填字段与枚举

用法:
    python3 validate_retrieval_spec.py
    python3 validate_retrieval_spec.py --plan <retrieval_plan.yaml>

退出码: 0 = 通过; 1 = 校验失败; 2 = 用法/文件错误。
本脚本只读, 永不修改任何文件。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / "references" / "retrieval-protocol.yaml"
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

PHASES = {"expansion", "audit", "convergence"}
LOOP_STEPS = ["formulate", "execute", "ingest", "audit", "revise_keywords", "decide"]
REVISION_ACTIONS = {
    "broaden",
    "narrow",
    "swap_axis",
    "swap_vocabulary",
    "swap_language",
    "swap_source_class",
}
BLINDSPOTS = {
    "source_blindspot",
    "lexical_blindspot",
    "modality_blindspot",
    "structural_blindspot",
    "temporal_blindspot",
    "language_blindspot",
    "stance_blindspot",
}
SOURCE_CLASSES = {"literature", "community", "practice", "sop"}
ROBUSTNESS_KEYS = {
    "channel_failure",
    "dedup",
    "source_grading",
    "degradation",
    "traceability",
}
ARTIFACTS = {"plan", "round", "followup"}
STOP_CONDITIONS = {
    "rho_converged",
    "theta_scene_shift",
    "budget_exhausted",
    "marginal_gain_below_epsilon",
    "blindspots_all_resolved",
}
PLAN_REQUIRED = [
    "plan_id",
    "task_boundary_ref",
    "phases",
    "sources",
    "queries",
    "budget",
    "stop_conditions",
]
QUERY_STYLES = {"sensitive", "specific"}


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def require_keys(
    failures: list[str], obj: dict, keys: set[str], where: str
) -> None:
    missing = sorted(keys - set(obj))
    if missing:
        fail(failures, f"{where} 缺少字段: {missing}")
    extra = sorted(set(obj) - keys)
    if extra:
        fail(failures, f"{where} 存在意料之外字段: {extra}")


def validate_protocol(failures: list[str]) -> dict | None:
    try:
        protocol = yaml.safe_load(PROTOCOL.read_text(encoding="utf-8"))
        if not isinstance(protocol, dict):
            raise ValueError("protocol 必须是映射")
    except Exception as exc:
        fail(failures, f"retrieval-protocol.yaml 解析失败: {exc}")
        return None

    meta = protocol.get("meta", {})
    if meta.get("module_id") != "extension-systematic-retrieval":
        fail(failures, "meta.module_id 必须是 extension-systematic-retrieval")
    if not SEMVER.fullmatch(str(meta.get("version", ""))):
        fail(failures, "meta.version 必须是语义化版本")
    if meta.get("lifecycle") != "experimental":
        fail(failures, "meta.lifecycle 必须是 experimental")

    phases = protocol.get("phases", {})
    require_keys(failures, phases, PHASES, "phases")
    for phase_id, phase in phases.items():
        if not isinstance(phase, dict):
            fail(failures, f"phases.{phase_id} 必须是映射")
            continue
        for key in ("name", "goal", "strategy", "acceptance"):
            if not str(phase.get(key, "")).strip():
                fail(failures, f"phases.{phase_id}.{key} 不能为空")
        actions = phase.get("actions")
        if not isinstance(actions, list) or not actions:
            fail(failures, f"phases.{phase_id}.actions 必须是非空列表")

    loop = protocol.get("loop", {})
    if loop.get("steps") != LOOP_STEPS:
        fail(failures, f"loop.steps 必须恰好是 {LOOP_STEPS}")
    try:
        default_rounds = int(loop.get("max_rounds_default", 0))
        hard_rounds = int(loop.get("max_rounds_hard", 0))
        if not 0 < default_rounds <= hard_rounds <= 5:
            fail(failures, "loop 轮次须满足 0 < default <= hard <= 5")
    except (TypeError, ValueError):
        fail(failures, "loop.max_rounds_default/hard 必须是整数")
    if not isinstance(loop.get("stop_conditions"), list) or not loop.get(
        "stop_conditions"
    ):
        fail(failures, "loop.stop_conditions 必须是非空列表")

    revisions = protocol.get("keyword_revision_actions", {})
    require_keys(failures, revisions, REVISION_ACTIONS | {"rule"}, "keyword_revision_actions")
    if not str(revisions.get("rule", "")).strip():
        fail(failures, "keyword_revision_actions.rule 不能为空")

    blindspots = protocol.get("blindspots", {})
    require_keys(failures, blindspots, BLINDSPOTS, "blindspots")
    for spot_id, spot in blindspots.items():
        if not isinstance(spot, dict):
            fail(failures, f"blindspots.{spot_id} 必须是映射")
            continue
        for key in ("description", "detection", "response"):
            if not str(spot.get(key, "")).strip():
                fail(failures, f"blindspots.{spot_id}.{key} 不能为空")

    sources = protocol.get("sources", {})
    require_keys(failures, sources, SOURCE_CLASSES | {"grading_note"}, "sources")
    for class_id, source in sources.items():
        if class_id == "grading_note":
            continue
        if not isinstance(source, dict):
            fail(failures, f"sources.{class_id} 必须是映射")
            continue
        for key in ("name", "evidence_grade", "notes"):
            if not str(source.get(key, "")).strip():
                fail(failures, f"sources.{class_id}.{key} 不能为空")
        for key in ("examples", "conventions"):
            items = source.get(key)
            if not isinstance(items, list) or not items:
                fail(failures, f"sources.{class_id}.{key} 必须是非空列表")

    design = protocol.get("query_design", {})
    require_keys(failures, design, {"convention", "designed", "pairing_rule"}, "query_design")
    for key in ("convention", "designed"):
        entry = design.get(key)
        if not isinstance(entry, dict):
            fail(failures, f"query_design.{key} 必须是映射")
            continue
        for field in ("description", "pros", "cons"):
            if not str(entry.get(field, "")).strip():
                fail(failures, f"query_design.{key}.{field} 不能为空")
        if not isinstance(entry.get("tools"), list) or not entry.get("tools"):
            fail(failures, f"query_design.{key}.tools 必须是非空列表")
    if not str(design.get("pairing_rule", "")).strip():
        fail(failures, "query_design.pairing_rule 不能为空")

    robustness = protocol.get("robustness", {})
    require_keys(failures, robustness, ROBUSTNESS_KEYS, "robustness")
    channel = robustness.get("channel_failure", {})
    for key in ("rule", "retry"):
        if not str(channel.get(key, "")).strip():
            fail(failures, f"robustness.channel_failure.{key} 不能为空")
    for key in ("dedup", "source_grading", "degradation", "traceability"):
        if not str(robustness.get(key, {}).get("rule", "")).strip():
            fail(failures, f"robustness.{key}.rule 不能为空")

    artifacts = protocol.get("artifacts", {})
    require_keys(failures, artifacts, ARTIFACTS, "artifacts")
    for name, artifact in artifacts.items():
        if not isinstance(artifact, dict):
            fail(failures, f"artifacts.{name} 必须是映射")
            continue
        for key in ("name", "path_pattern"):
            if not str(artifact.get(key, "")).strip():
                fail(failures, f"artifacts.{name}.{key} 不能为空")
        fields = artifact.get("required_fields")
        if not isinstance(fields, list) or not fields:
            fail(failures, f"artifacts.{name}.required_fields 必须是非空列表")

    constraints = protocol.get("frozen_constraints")
    if not isinstance(constraints, list) or not constraints:
        fail(failures, "frozen_constraints 必须是非空列表")

    return protocol


def validate_plan(path: Path, failures: list[str]) -> None:
    try:
        plan = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(plan, dict):
            raise ValueError("plan 必须是映射")
    except Exception as exc:
        fail(failures, f"{path.name} 解析失败: {exc}")
        return

    missing = [key for key in PLAN_REQUIRED if key not in plan]
    for key in missing:
        fail(failures, f"计划缺少必填字段: {key}")

    plan_phases = plan.get("phases")
    if not isinstance(plan_phases, list) or not plan_phases:
        fail(failures, "phases 必须是非空列表")
    else:
        bad = sorted(set(plan_phases) - PHASES)
        if bad:
            fail(failures, f"phases 含非法值: {bad}")

    sources = plan.get("sources")
    if not isinstance(sources, dict):
        fail(failures, "sources 必须是映射")
    else:
        bad = sorted(set(sources) - SOURCE_CLASSES)
        if bad:
            fail(failures, f"sources 含非法来源类别: {bad}")

    queries = plan.get("queries")
    if not isinstance(queries, list) or not queries:
        fail(failures, "queries 必须是非空列表")
    else:
        for index, query in enumerate(queries):
            if not isinstance(query, dict):
                fail(failures, f"queries[{index}] 必须是映射")
                continue
            for key in ("query_id", "text"):
                if not str(query.get(key, "")).strip():
                    fail(failures, f"queries[{index}].{key} 不能为空")
            if query.get("phase") not in PHASES:
                fail(failures, f"queries[{index}].phase 非法: {query.get('phase')}")
            if query.get("source_class") not in SOURCE_CLASSES:
                fail(
                    failures,
                    f"queries[{index}].source_class 非法: {query.get('source_class')}",
                )
            if query.get("style") not in QUERY_STYLES:
                fail(failures, f"queries[{index}].style 非法: {query.get('style')}")

    budget = plan.get("budget", {})
    max_rounds = budget.get("max_rounds")
    if not isinstance(max_rounds, int) or isinstance(max_rounds, bool):
        fail(failures, "budget.max_rounds 必须是整数")
    elif not 0 < max_rounds <= 5:
        fail(failures, "budget.max_rounds 须满足 0 < max_rounds <= 5")

    stops = plan.get("stop_conditions")
    if not isinstance(stops, list) or not stops:
        fail(failures, "stop_conditions 必须是非空列表")
    else:
        bad = sorted(set(stops) - STOP_CONDITIONS)
        if bad:
            fail(failures, f"stop_conditions 含非法值: {bad}")

    checklist = plan.get("blindspot_checklist", [])
    if not isinstance(checklist, list):
        fail(failures, "blindspot_checklist 必须是列表")
    else:
        bad = sorted(set(checklist) - BLINDSPOTS)
        if bad:
            fail(failures, f"blindspot_checklist 含非法值: {bad}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="校验系统化检索分支协议结构与检索计划 (只读)"
    )
    parser.add_argument(
        "--plan",
        metavar="FILE",
        help="校验一份运行时 RetrievalPlan YAML 文件",
    )
    args = parser.parse_args()

    failures: list[str] = []
    protocol = validate_protocol(failures)

    if args.plan:
        plan_path = Path(args.plan)
        if not plan_path.is_file():
            print(f"ERROR: 计划文件不存在: {plan_path}", file=sys.stderr)
            return 2
        validate_plan(plan_path, failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        print(f"{len(failures)} validation failure(s)")
        return 1

    if protocol is not None:
        print(
            "PASS: retrieval protocol structure is internally consistent "
            "(3 phases / 6-step loop / 7 blindspots / 4 source classes)"
        )
    if args.plan:
        print(f"PASS: retrieval plan {args.plan} conforms to schema")
    print("NOTE: 检索语义质量 (命中是否充分) 需人工复核, 本脚本只验证结构")
    return 0


if __name__ == "__main__":
    sys.exit(main())
