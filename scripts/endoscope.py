#!/usr/bin/env python3
"""Endoscope 0.2 reference controller.

The controller is intentionally small and dependency-free. It coordinates:
TaskProfile -> Normalization Shadow Ledger -> probes -> minimal revival -> E/S/O gates
-> Bloodtesting records -> calibration candidates.

It does not claim calibrated error probabilities, does not mutate model weights, and
never auto-promotes a learned policy. Optional language adapters (currently base R)
may enrich observations without becoming a hard dependency.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

PROTOCOL_VERSION = "0.2.0"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILES = ROOT / "references" / "endoscope-task-profiles.json"
R_ADAPTER = ROOT / "scripts" / "endoscope_r.R"

GATE_EXECUTION = {"OPEN", "CONTINUE_DIAGNOSTIC", "PAUSE_BEFORE_SIDE_EFFECT", "STOP"}
GATE_STATE = {"OPEN", "FILTERED", "QUARANTINED", "DISCARD"}
GATE_OUTPUT = {"OPEN", "REVIEW_REQUIRED", "BLOCKED", "REPLACE"}
COST_RANK = {"cheap": 0, "medium": 1, "expensive": 2, "unknown": 3}

PATTERNS: dict[str, re.Pattern[str]] = {
    "destructive_write": re.compile(
        r"\b(os\.remove|os\.unlink|shutil\.rmtree|rm\s+-rf|DROP\s+TABLE|TRUNCATE\s+TABLE|bulk_replace|file\.remove|unlink\s*\()\b",
        re.I,
    ),
    "external_write": re.compile(
        r"\b(UPDATE|INSERT|DELETE\s+FROM|write_csv|to_csv|write\.csv|write\.table|writeLines|saveRDS|dbExecute|open\([^\n]*['\"]w|publish\s*\()",
        re.I,
    ),
    "dynamic_exec": re.compile(r"\b(eval|exec|source|system|system2)\s*\(", re.I),
    "shell": re.compile(r"shell\s*=\s*True|subprocess\.(run|Popen)|os\.system", re.I),
    "concurrency": re.compile(r"ThreadPool|ProcessPool|threading|multiprocessing|future::|parallel::", re.I),
    "broad_exception": re.compile(r"except\s*:\s*$|except\s+Exception", re.M),
    "r_global_assign": re.compile(r"<<-|\.GlobalEnv|assign\s*\(", re.I),
    "r_coercion_sensitive": re.compile(r"\bas\.(numeric|integer)\s*\(", re.I),
    "na_sensitive_branch": re.compile(r"\bif\s*\([^\n]*[><=!]=?[^\n]*\)", re.I),
    "credential_or_permission": re.compile(r"\b(chmod|chown|setfacl|secret|token|api[_-]?key|permission|iam)\b", re.I),
}

SEVERITY = {
    "destructive_write": "critical",
    "external_write": "high",
    "dynamic_exec": "high",
    "shell": "high",
    "concurrency": "high",
    "credential_or_permission": "critical",
    "broad_exception": "medium",
    "r_global_assign": "medium",
    "r_coercion_sensitive": "medium",
    "na_sensitive_branch": "medium",
    "parse_error": "high",
    "r_adapter_unavailable": "info",
}


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join("" if p is None else str(p) for p in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]}"


def require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def load_profiles(path: Path = DEFAULT_PROFILES) -> dict[str, Any]:
    data = require_mapping(load_json(path), "profiles")
    if data.get("schema_version") != PROTOCOL_VERSION:
        raise ValueError(
            f"profile schema_version must be {PROTOCOL_VERSION}, got {data.get('schema_version')!r}"
        )
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("profiles.profiles must be a non-empty object")
    return data


def compile_profile(task_family: str, path: Path = DEFAULT_PROFILES) -> dict[str, Any]:
    registry = load_profiles(path)
    profiles = registry["profiles"]
    if task_family not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(f"unknown task_family {task_family!r}; choose one of: {available}")
    profile = dict(profiles[task_family])
    profile["task_family"] = task_family
    profile["profile_id"] = stable_id("pt", task_family, registry["schema_version"])
    profile["schema_version"] = registry["schema_version"]
    return profile


def ast_depth(node: ast.AST) -> int:
    children = list(ast.iter_child_nodes(node))
    return 1 if not children else 1 + max(ast_depth(child) for child in children)


def python_ast_observation(text: str) -> dict[str, Any]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {
            "engine": "python-ast",
            "parse_ok": False,
            "parse_error": {"line": exc.lineno, "offset": exc.offset, "message": exc.msg},
            "nesting": None,
            "imports": [],
            "definitions": [],
        }
    imports: list[str] = []
    definitions: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions.append(node.name)
    return {
        "engine": "python-ast",
        "parse_ok": True,
        "parse_error": None,
        "nesting": ast_depth(tree),
        "imports": sorted(set(x for x in imports if x)),
        "definitions": definitions,
    }


def brace_depth(text: str) -> int:
    depth = best = 0
    for char in text:
        if char == "{":
            depth += 1
            best = max(best, depth)
        elif char == "}":
            depth = max(0, depth - 1)
    return best


def regex_findings(text: str, source: str = "static-regex") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append(
                {
                    "signal": name,
                    "severity": SEVERITY.get(name, "medium"),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "match": match.group(0)[:160],
                    "source": source,
                    "evidence_type": "observed_source",
                }
            )
    return findings


def run_r_adapter(path: Path) -> dict[str, Any] | None:
    rscript = shutil.which("Rscript")
    if not rscript or not R_ADAPTER.exists():
        return None
    proc = subprocess.run(
        [rscript, str(R_ADAPTER), "probe", str(path)],
        text=True,
        capture_output=True,
        timeout=20,
    )
    if proc.returncode != 0:
        return {
            "engine": "base-r",
            "parse_ok": False,
            "adapter_error": proc.stderr.strip() or f"R adapter exited {proc.returncode}",
            "signals": [],
        }
    try:
        value = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "engine": "base-r",
            "parse_ok": False,
            "adapter_error": f"invalid adapter JSON: {exc}",
            "signals": [],
        }
    return require_mapping(value, "R adapter output")


def infer_scope(lines: int) -> int:
    if lines <= 50:
        return 0
    if lines <= 250:
        return 1
    if lines <= 1000:
        return 2
    return 3


def probe_source(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    findings = regex_findings(text)
    language = "generic"
    semantic: dict[str, Any] = {
        "engine": "generic",
        "parse_ok": None,
        "parse_error": None,
        "nesting": brace_depth(text),
    }
    adapter_status = "not_applicable"

    if suffix == ".py":
        language = "python"
        semantic = python_ast_observation(text)
    elif suffix in {".r", ".rscript"}:
        language = "r"
        r_result = run_r_adapter(path)
        if r_result is None:
            adapter_status = "unavailable_fallback_static"
            findings.append(
                {
                    "signal": "r_adapter_unavailable",
                    "severity": "info",
                    "line": None,
                    "match": "Rscript not available; static fallback used",
                    "source": "adapter",
                    "evidence_type": "environment_observation",
                }
            )
            semantic = {
                "engine": "generic-r-fallback",
                "parse_ok": None,
                "parse_error": None,
                "nesting": brace_depth(text),
            }
        else:
            adapter_status = "available"
            semantic = {
                "engine": r_result.get("engine", "base-r"),
                "parse_ok": r_result.get("parse_ok"),
                "parse_error": r_result.get("parse_error"),
                "nesting": r_result.get("nesting", brace_depth(text)),
                "expression_count": r_result.get("expression_count"),
            }
            for item in r_result.get("signals", []):
                if isinstance(item, dict):
                    signal = str(item.get("signal", "r_runtime_signal"))
                    findings.append(
                        {
                            "signal": signal,
                            "severity": item.get("severity", SEVERITY.get(signal, "medium")),
                            "line": item.get("line"),
                            "match": item.get("match", "")[:160],
                            "source": "base-r",
                            "evidence_type": "observed_source",
                        }
                    )

    if semantic.get("parse_ok") is False:
        findings.append(
            {
                "signal": "parse_error",
                "severity": "high",
                "line": (semantic.get("parse_error") or {}).get("line"),
                "match": (semantic.get("parse_error") or {}).get("message", "parse error"),
                "source": semantic.get("engine"),
                "evidence_type": "parser_observation",
            }
        )

    seen: set[tuple[Any, ...]] = set()
    deduped: list[dict[str, Any]] = []
    for item in findings:
        key = (item.get("signal"), item.get("line"), item.get("match"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    irreversible = any(
        item["signal"] in {"destructive_write", "credential_or_permission"} for item in deduped
    )
    high_or_critical = sum(item["severity"] in {"high", "critical"} for item in deduped)
    lines = len(text.splitlines())
    return {
        "protocol_version": PROTOCOL_VERSION,
        "probe_id": stable_id("probe", path.as_posix(), hashlib.sha256(text.encode()).hexdigest()),
        "target": {"kind": "file", "path": str(path), "language": language},
        "engine": semantic.get("engine"),
        "adapter_status": adapter_status,
        "observations": deduped,
        "syntax": semantic,
        "summary": {
            "lines": lines,
            "scope_hint": infer_scope(lines),
            "signal_count": len(deduped),
            "high_or_critical": high_or_critical,
            "irreversible_write": irreversible,
        },
    }


def normalize_omitted(space: str, stage: str, boundary_id: str, omitted: Any, recovery_refs: Any) -> list[dict[str, Any]]:
    if omitted is None:
        return []
    if not isinstance(omitted, list):
        raise ValueError(f"{stage}.omitted_features must be a list")
    refs = recovery_refs if isinstance(recovery_refs, list) else []
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(omitted):
        if isinstance(raw, dict):
            feature = str(raw.get("feature") or raw.get("name") or raw.get("id") or f"item_{index}")
            recovery_ref = raw.get("recovery_ref")
            omitted_reason = str(raw.get("omitted_reason", "indifferent"))
            relation = raw.get("relation_to_active", [])
            source_ref = raw.get("source_ref")
            cost = str(raw.get("recovery_cost", "unknown"))
            sensitivity = str(raw.get("sensitivity", "normal"))
        else:
            feature = str(raw)
            recovery_ref = refs[index] if index < len(refs) else None
            omitted_reason = "indifferent"
            relation = []
            source_ref = None
            cost = "unknown"
            sensitivity = "normal"
        if isinstance(relation, str):
            relation = [relation]
        elif not isinstance(relation, list):
            relation = []
        result.append({
            "shadow_id": stable_id("sh", boundary_id, space, stage, feature, recovery_ref),
            "boundary_id": boundary_id,
            "space": space,
            "stage": stage,
            "feature": feature,
            "source_ref": source_ref,
            "recovery_ref": recovery_ref,
            "omitted_reason": omitted_reason,
            "relation_to_active": [str(x) for x in relation],
            "recovery_cost": cost if cost in COST_RANK else "unknown",
            "sensitivity": sensitivity,
            "status": "shadow",
        })
    return result


def build_shadow_ledger(snapshot: dict[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    boundary_id = "unknown"
    for key, space, stage in (
        ("meta_view", "meta", "meta_normalization"),
        ("mutual_view", "hu", "hu_normalization"),
        ("focus_view", "focus", "n_focus"),
        ("condense_view", "condense", "condense"),
        ("output_view", "output", "output_compiler"),
    ):
        view = snapshot.get(key)
        if not isinstance(view, dict):
            continue
        boundary_id = str(view.get("boundary_id") or snapshot.get("boundary_id") or boundary_id)
        items.extend(normalize_omitted(space, stage, boundary_id, view.get("omitted_features"), view.get("recovery_refs")))
    return {
        "protocol_version": PROTOCOL_VERSION,
        "ledger_id": stable_id("nsl", boundary_id, len(items), *(x["shadow_id"] for x in items)),
        "boundary_id": boundary_id,
        "items": items,
        "summary": dict(Counter(item["space"] for item in items)),
    }


def tokens(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        result: set[str] = set()
        for item in value:
            result |= tokens(item)
        return result
    return {x for x in re.split(r"[^a-z0-9_]+", str(value).lower()) if x}


def event_features(event: dict[str, Any]) -> set[str]:
    values: list[Any] = []
    for key in ("signal", "signals", "features", "relation_mismatch", "reason", "locus"):
        if key in event:
            values.append(event[key])
    return tokens(values)


def watched_features(profile: dict[str, Any]) -> set[str]:
    watch = profile.get("shadow_watch", {})
    values: list[Any] = []
    if isinstance(watch, dict):
        values.extend(watch.values())
    else:
        values.append(watch)
    return tokens(values)


def revive_shadow(ledger: dict[str, Any], profile: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    evt = event_features(event)
    watched = watched_features(profile)
    recovery = profile.get("recovery", {}) if isinstance(profile.get("recovery"), dict) else {}
    max_items = int(recovery.get("max_items", 6))
    max_cost = str(recovery.get("max_cost", "expensive"))
    max_cost_rank = COST_RANK.get(max_cost, 2)

    candidates: list[dict[str, Any]] = []
    for item in ledger.get("items", []):
        if not isinstance(item, dict):
            continue
        feature_tokens = tokens(item.get("feature"))
        relation_tokens = tokens(item.get("relation_to_active"))
        score = 0
        reasons: list[str] = []
        if feature_tokens & evt:
            score += 5
            reasons.append("event_feature_match")
        if relation_tokens & evt:
            score += 4
            reasons.append("active_relation_match")
        evidence_match = bool(feature_tokens & evt or relation_tokens & evt)
        if feature_tokens & watched and evidence_match:
            score += 2
            reasons.append("task_profile_watch")
        if item.get("omitted_reason") == "conflicting" and evt:
            score += 2
            reasons.append("conflicting_shadow")
        elif item.get("omitted_reason") == "insufficient" and evidence_match:
            score += 1
            reasons.append("insufficient_shadow")
        if item.get("space") == "hu" and evidence_match and ({"relation", "mismatch", "correlation", "dependency"} & evt):
            score += 1
            reasons.append("hu_event_alignment")
        cost = COST_RANK.get(str(item.get("recovery_cost", "unknown")), 3)
        if cost > max_cost_rank:
            continue
        if score > 0 and (evidence_match or (item.get("omitted_reason") == "conflicting" and evt)):
            candidates.append({
                "shadow_id": item.get("shadow_id"),
                "feature": item.get("feature"),
                "recovery_ref": item.get("recovery_ref"),
                "revival_rank": score,
                "rank_is_probability": False,
                "reasons": reasons,
                "recovery_cost": item.get("recovery_cost"),
            })
    candidates.sort(key=lambda x: (-int(x["revival_rank"]), COST_RANK.get(str(x["recovery_cost"]), 3), str(x["shadow_id"])))
    selected = candidates[:max_items]
    return {
        "protocol_version": PROTOCOL_VERSION,
        "event_id": event.get("event_id") or stable_id("evt", json.dumps(event, sort_keys=True, ensure_ascii=False)),
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "selected": selected,
        "recovery_policy": {"max_items": max_items, "max_cost": max_cost},
    }


def gate_decision(scope: int, blast: int, uncertainty: int, dependency: int, *, irreversible: bool = False, tainted: bool = False, revival_count: int = 0, explicit_block: bool = False) -> dict[str, Any]:
    axes = {"S": scope, "B": blast, "U": uncertainty, "D": dependency}
    if any(not isinstance(v, int) or v < 0 or v > 3 for v in axes.values()):
        raise ValueError("S/B/U/D must each be integer 0..3")
    score = 0.25 * scope + 0.35 * blast + 0.25 * uncertainty + 0.15 * dependency
    reasons: list[str] = []
    if score <= 0.75:
        execution, state, output, ceiling = "OPEN", "OPEN", "OPEN", "PATCH_LEAF"
    elif score <= 1.50:
        execution, state, output, ceiling = "OPEN", "FILTERED", "REVIEW_REQUIRED", "PATCH_LOCAL"
    elif score <= 2.25:
        execution, state, output, ceiling = "CONTINUE_DIAGNOSTIC", "QUARANTINED", "BLOCKED", "PATCH_LEAF"
    else:
        execution, state, output, ceiling = "CONTINUE_DIAGNOSTIC", "QUARANTINED", "BLOCKED", "NO_TOUCH"
    if tainted or revival_count > 0 or explicit_block:
        state = "QUARANTINED"
        output = "BLOCKED"
        reasons.append("tainted_or_shadow_revival")
        if execution == "OPEN":
            execution = "CONTINUE_DIAGNOSTIC"
    if irreversible:
        execution, state, output, ceiling = "PAUSE_BEFORE_SIDE_EFFECT", "QUARANTINED", "BLOCKED", "NO_TOUCH"
        reasons.append("irreversible_side_effect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "risk_axes": axes,
        "heuristic_R": round(score, 3),
        "calibrated_probability": None,
        "execution_gate": execution,
        "state_gate": state,
        "output_gate": output,
        "max_intervention": ceiling,
        "reasons": reasons,
        "final_decoder_allowed": output == "OPEN",
    }


def derive_axes(probe: dict[str, Any] | None, profile: dict[str, Any]) -> dict[str, int]:
    defaults = profile.get("risk_defaults", {}) if isinstance(profile.get("risk_defaults"), dict) else {}
    scope = int(defaults.get("S", 1)); blast = int(defaults.get("B", 1)); uncertainty = int(defaults.get("U", 1)); dependency = int(defaults.get("D", 1))
    if probe:
        summary = probe.get("summary", {})
        scope = max(scope, int(summary.get("scope_hint", 0)))
        observations = probe.get("observations", [])
        severities = {item.get("severity") for item in observations if isinstance(item, dict)}
        if "critical" in severities: blast = max(blast, 3)
        elif "high" in severities: blast = max(blast, 2)
        if probe.get("syntax", {}).get("parse_ok") is False: uncertainty = max(uncertainty, 3)
        elif probe.get("adapter_status") == "unavailable_fallback_static": uncertainty = max(uncertainty, 1)
        nesting = probe.get("syntax", {}).get("nesting")
        if isinstance(nesting, int):
            if nesting >= 16: dependency = max(dependency, 3)
            elif nesting >= 9: dependency = max(dependency, 2)
    return {"S": min(scope, 3), "B": min(blast, 3), "U": min(uncertainty, 3), "D": min(dependency, 3)}


def probe_event(probe: dict[str, Any]) -> dict[str, Any]:
    signals = [item.get("signal") for item in probe.get("observations", []) if isinstance(item, dict) and item.get("signal")]
    return {
        "event_id": stable_id("evt", probe.get("probe_id"), *signals),
        "event_type": "probe_observation",
        "signals": signals,
        "features": signals,
        "evidence_type": "observed_source",
        "locus": probe.get("target", {}).get("path"),
    }


def rho_event(task_family: str, probe: dict[str, Any] | None, revival: dict[str, Any] | None, gate: dict[str, Any]) -> dict[str, Any]:
    signals = []
    if probe:
        signals = [x.get("signal") for x in probe.get("observations", []) if isinstance(x, dict) and x.get("signal")]
    revived = 0 if revival is None else int(revival.get("selected_count", 0))
    return {
        "event_type": "endoscope_attention_event",
        "task_family": task_family,
        "observed_signals": signals,
        "shadow_revival_count": revived,
        "evidence_status": "observed_or_recovered",
        "rho_value": None,
        "recommended_attention": {
            "continue_compute": "low" if gate["execution_gate"] in {"STOP", "PAUSE_BEFORE_SIDE_EFFECT"} else "high",
            "inspect_shadow": "high" if revived else "medium",
            "inspect_side_effect": "high" if gate["execution_gate"] == "PAUSE_BEFORE_SIDE_EFFECT" else "low",
            "generate_final_interpretation": "high" if gate["output_gate"] == "OPEN" else "low",
        },
    }


def run_pipeline(task_family: str, profiles_path: Path, source: Path | None, snapshot: Path | None, event: dict[str, Any] | None, axis_overrides: dict[str, int | None], tainted: bool, irreversible: bool) -> dict[str, Any]:
    profile = compile_profile(task_family, profiles_path)
    probe = probe_source(source) if source else None
    ledger = build_shadow_ledger(require_mapping(load_json(snapshot), "snapshot")) if snapshot else None
    if event is None and probe is not None: event = probe_event(probe)
    elif event is None: event = {"event_id": stable_id("evt", task_family, "no_observation"), "signals": [], "features": []}
    revival = revive_shadow(ledger, profile, event) if ledger else None
    axes = derive_axes(probe, profile)
    for key, value in axis_overrides.items():
        if value is not None: axes[key] = int(value)
    inferred_irreversible = bool(probe and probe.get("summary", {}).get("irreversible_write"))
    inferred_tainted = bool(revival and revival.get("selected_count"))
    semantic_taint_signals = {"parse_error", "r_coercion_sensitive", "na_sensitive_branch", "broad_exception"}
    if probe:
        inferred_tainted = inferred_tainted or any(item.get("signal") in semantic_taint_signals for item in probe.get("observations", []) if isinstance(item, dict))
    gate = gate_decision(axes["S"], axes["B"], axes["U"], axes["D"], irreversible=irreversible or inferred_irreversible, tainted=tainted or inferred_tainted, revival_count=0 if revival is None else int(revival.get("selected_count", 0)))
    return {
        "protocol_version": PROTOCOL_VERSION,
        "task_profile": profile,
        "probe": probe,
        "shadow_ledger": ledger,
        "event": event,
        "revival": revival,
        "gate": gate,
        "rho_attention_event": rho_event(task_family, probe, revival, gate),
        "delivery": {"final_decoder_allowed": gate["final_decoder_allowed"], "next": "REVIEW_OR_RECOVER" if gate["output_gate"] != "OPEN" else "GENERATE_FINAL_RESPONSE"},
    }


def validate_blood_record(record: dict[str, Any]) -> None:
    required = {"record_id", "task_family", "signals", "probe_flagged", "true_bleed", "gate_expected", "gate_actual", "recovery", "metrics"}
    missing = sorted(required - set(record))
    if missing: raise ValueError(f"blood record missing: {missing}")
    for field in ("gate_expected", "gate_actual"):
        gate = require_mapping(record[field], field)
        if gate.get("execution") not in GATE_EXECUTION: raise ValueError(f"{field}.execution invalid")
        if gate.get("state") not in GATE_STATE: raise ValueError(f"{field}.state invalid")
        if gate.get("output") not in GATE_OUTPUT: raise ValueError(f"{field}.output invalid")


def append_blood_record(record: dict[str, Any], path: Path) -> dict[str, Any]:
    validate_blood_record(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return {"appended": True, "path": str(path), "record_id": record["record_id"]}


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip(): continue
        try: item = json.loads(raw)
        except json.JSONDecodeError as exc: raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        yield require_mapping(item, f"record line {line_no}")


def calibrate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records: raise ValueError("at least one blood record is required")
    for record in records: validate_blood_record(record)
    def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(items)
        false_alarm = sum(bool(x["probe_flagged"]) and not bool(x["true_bleed"]) for x in items)
        missed = sum((not bool(x["probe_flagged"])) and bool(x["true_bleed"]) for x in items)
        gate_correct = 0; recovered = effective = 0; avoidable = 0.0; signal_counts: Counter[str] = Counter()
        for x in items:
            exp, act = x["gate_expected"], x["gate_actual"]
            gate_correct += exp.get("execution") == act.get("execution") and exp.get("state") == act.get("state") and exp.get("output") == act.get("output")
            rec = x.get("recovery", {}); recovered += int(rec.get("recovered_items", 0) or 0); effective += int(rec.get("effective_items", 0) or 0)
            avoidable += float(x.get("metrics", {}).get("avoidable_output_tokens", 0) or 0)
            signal_counts.update(str(s) for s in x.get("signals", []) if s)
        metrics = {
            "records": n,
            "false_alarm_rate": round(false_alarm / n, 4),
            "missed_bleed_rate": round(missed / n, 4),
            "gate_accuracy": round(gate_correct / n, 4),
            "recovery_efficiency": None if recovered == 0 else round(effective / recovered, 4),
            "avg_avoidable_output_tokens": round(avoidable / n, 2),
            "top_signals": signal_counts.most_common(10),
        }
        if n < 10: status = "collect_more"
        elif metrics["false_alarm_rate"] <= 0.15 and metrics["missed_bleed_rate"] <= 0.10 and metrics["gate_accuracy"] >= 0.90: status = "eligible_for_shadow_replay"
        else: status = "recalibrate_candidate"
        metrics["policy_candidate_status"] = status; metrics["auto_promote"] = False
        return metrics
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records: by_family[str(record["task_family"])].append(record)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "overall": summarize(records),
        "by_task_family": {family: summarize(items) for family, items in sorted(by_family.items())},
        "promotion_rule": "candidate -> shadow replay -> A/B review -> explicit promotion",
    }


def selftest() -> dict[str, Any]:
    checks: dict[str, str] = {}
    profiles = load_profiles(DEFAULT_PROFILES); checks["profiles"] = f"PASS:{len(profiles['profiles'])}"
    sample_snapshot = {
        "meta_view": {"boundary_id": "bt_demo", "omitted_features": [{"feature": "sample_size", "recovery_ref": "source://meta/1", "recovery_cost": "cheap"}]},
        "mutual_view": {"boundary_id": "bt_demo", "omitted_features": [{"feature": "feature_correlation", "recovery_ref": "source://hu/7", "relation_to_active": ["support_stability"], "recovery_cost": "cheap"}]},
    }
    ledger = build_shadow_ledger(sample_snapshot)
    if len(ledger["items"]) != 2: raise AssertionError("shadow ledger item count")
    checks["shadow"] = "PASS"
    profile = compile_profile("statistical_modeling")
    event = {"signals": ["support_instability"], "features": ["feature_correlation"]}
    revival = revive_shadow(ledger, profile, event)
    if len(revival["selected"]) != 1 or revival["selected"][0]["feature"] != "feature_correlation": raise AssertionError("minimal revival failed")
    checks["revival"] = "PASS"
    if gate_decision(0, 0, 0, 0)["output_gate"] != "OPEN": raise AssertionError("low-risk gate")
    if gate_decision(0, 0, 0, 0, tainted=True)["output_gate"] != "BLOCKED": raise AssertionError("tainted output gate")
    if gate_decision(0, 0, 0, 0, irreversible=True)["execution_gate"] != "PAUSE_BEFORE_SIDE_EFFECT": raise AssertionError("irreversible execution gate")
    checks["gates"] = "PASS"
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "sample.py"; p.write_text("import os\ndef f(x):\n    if x > 0:\n        os.remove(x)\n", encoding="utf-8")
        probe = probe_source(p)
        if not probe["summary"]["irreversible_write"]: raise AssertionError("python destructive write probe")
        checks["python_probe"] = "PASS"
        r = Path(tmp) / "sample.R"; r.write_text('x <- as.integer("x")\nif (x > 5) print(x)\n', encoding="utf-8")
        r_probe = probe_source(r)
        if not any(x.get("signal") == "na_sensitive_branch" for x in r_probe["observations"]): raise AssertionError("R static fallback probe")
        checks["r_probe"] = "PASS" if r_probe["adapter_status"] == "available" else "PASS:fallback"
    record = {
        "record_id": "br_demo", "task_family": "statistical_modeling", "signals": ["support_instability"], "probe_flagged": True, "true_bleed": True,
        "gate_expected": {"execution": "CONTINUE_DIAGNOSTIC", "state": "QUARANTINED", "output": "BLOCKED"},
        "gate_actual": {"execution": "CONTINUE_DIAGNOSTIC", "state": "QUARANTINED", "output": "BLOCKED"},
        "recovery": {"recovered_items": 1, "effective_items": 1}, "metrics": {"avoidable_output_tokens": 100},
    }
    calibration = calibrate_records([record])
    if calibration["overall"]["gate_accuracy"] != 1.0: raise AssertionError("blood calibration")
    checks["blood"] = "PASS"
    return {"protocol_version": PROTOCOL_VERSION, "status": "PASS", "checks": checks}


def parse_event_arg(event_file: Path | None, event_json: str | None) -> dict[str, Any] | None:
    if event_file and event_json: raise ValueError("use only one of --event-file and --event-json")
    if event_file: return require_mapping(load_json(event_file), "event")
    if event_json: return require_mapping(json.loads(event_json), "event")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Endoscope 0.2 shadow-aware probe and gate controller")
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES, help="Task profile registry JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    p_profile = sub.add_parser("profile", help="Compile one deterministic TaskProfile"); p_profile.add_argument("task_family")
    p_probe = sub.add_parser("probe", help="Probe one source file without modifying it"); p_probe.add_argument("path", type=Path)
    p_shadow = sub.add_parser("shadow-build", help="Build NSL from normalization snapshot JSON"); p_shadow.add_argument("snapshot", type=Path)
    p_revive = sub.add_parser("revive", help="Rank minimal shadow recovery candidates"); p_revive.add_argument("ledger", type=Path); p_revive.add_argument("--task-family", required=True); p_revive.add_argument("--event-file", type=Path); p_revive.add_argument("--event-json")
    p_gate = sub.add_parser("gate", help="Compute independent Execution/State/Output gates")
    for name in ("scope", "blast", "uncertainty", "dependency"): p_gate.add_argument(f"--{name}", type=int, required=True)
    p_gate.add_argument("--irreversible", action="store_true"); p_gate.add_argument("--tainted", action="store_true"); p_gate.add_argument("--revival-count", type=int, default=0); p_gate.add_argument("--explicit-block", action="store_true")
    p_pipeline = sub.add_parser("pipeline", help="Run TaskProfile -> probe -> NSL -> revival -> E/S/O")
    p_pipeline.add_argument("--task-family", required=True); p_pipeline.add_argument("--source", type=Path); p_pipeline.add_argument("--snapshot", type=Path); p_pipeline.add_argument("--event-file", type=Path); p_pipeline.add_argument("--event-json")
    for name in ("scope", "blast", "uncertainty", "dependency"): p_pipeline.add_argument(f"--{name}", type=int)
    p_pipeline.add_argument("--irreversible", action="store_true"); p_pipeline.add_argument("--tainted", action="store_true")
    p_record = sub.add_parser("blood-record", help="Validate and append one Bloodtesting JSON record"); p_record.add_argument("record", type=Path); p_record.add_argument("--append", type=Path, required=True)
    p_calibrate = sub.add_parser("calibrate", help="Summarize Bloodtesting JSONL without auto-promoting policy"); p_calibrate.add_argument("records", type=Path)
    sub.add_parser("selftest", help="Run deterministic reference self-tests")
    args = parser.parse_args()
    try:
        if args.command == "profile": result = compile_profile(args.task_family, args.profiles)
        elif args.command == "probe": result = probe_source(args.path)
        elif args.command == "shadow-build": result = build_shadow_ledger(require_mapping(load_json(args.snapshot), "snapshot"))
        elif args.command == "revive": result = revive_shadow(require_mapping(load_json(args.ledger), "ledger"), compile_profile(args.task_family, args.profiles), parse_event_arg(args.event_file, args.event_json) or {"signals": [], "features": []})
        elif args.command == "gate": result = gate_decision(args.scope, args.blast, args.uncertainty, args.dependency, irreversible=args.irreversible, tainted=args.tainted, revival_count=args.revival_count, explicit_block=args.explicit_block)
        elif args.command == "pipeline": result = run_pipeline(args.task_family, args.profiles, args.source, args.snapshot, parse_event_arg(args.event_file, args.event_json), {"S": args.scope, "B": args.blast, "U": args.uncertainty, "D": args.dependency}, args.tainted, args.irreversible)
        elif args.command == "blood-record": result = append_blood_record(require_mapping(load_json(args.record), "blood record"), args.append)
        elif args.command == "calibrate": result = calibrate_records(list(iter_jsonl(args.records)))
        else: result = selftest()
        emit(result); return 0
    except (ValueError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        emit({"protocol_version": PROTOCOL_VERSION, "status": "ERROR", "error": str(exc)}); return 2


if __name__ == "__main__":
    raise SystemExit(main())
