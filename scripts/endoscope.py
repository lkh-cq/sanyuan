#!/usr/bin/env python3
"""Lightweight Endoscope controller for code-risk probing and output gating.

This is deliberately heuristic. It emits observations and intervention ceilings;
it does not claim error probabilities and does not modify high-risk code.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any


PATTERNS: dict[str, re.Pattern[str]] = {
    "destructive_write": re.compile(
        r"\b(os\.remove|os\.unlink|shutil\.rmtree|rm\s+-rf|DROP\s+TABLE|TRUNCATE\s+TABLE|bulk_replace)\b",
        re.I,
    ),
    "external_write": re.compile(
        r"\b(UPDATE|INSERT|DELETE\s+FROM|write_csv|to_csv|writeLines|saveRDS|open\([^\n]*['\"]w|publish\s*\()",
        re.I,
    ),
    "dynamic_exec": re.compile(r"\b(eval|exec|source|system|system2)\s*\(", re.I),
    "shell": re.compile(r"shell\s*=\s*True|subprocess\.(run|Popen)|os\.system", re.I),
    "concurrency": re.compile(r"ThreadPool|ProcessPool|threading|multiprocessing|future::|parallel::", re.I),
    "broad_exception": re.compile(r"except\s*:\s*$|except\s+Exception", re.M),
    "na_sensitive_branch": re.compile(r"\bif\s*\([^\n]*[><=!]=?[^\n]*\)", re.I),
}


def ast_depth(node: ast.AST) -> int:
    children = list(ast.iter_child_nodes(node))
    if not children:
        return 1
    return 1 + max(ast_depth(child) for child in children)


def brace_depth(text: str) -> int:
    depth = best = 0
    for char in text:
        if char == "{":
            depth += 1
            best = max(best, depth)
        elif char == "}":
            depth = max(0, depth - 1)
    return best


def probe(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[dict[str, Any]] = []

    for name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append({"signal": name, "line": line, "match": match.group(0)[:120]})

    syntax = "generic"
    nesting = brace_depth(text)
    parse_error = None
    if path.suffix == ".py":
        try:
            tree = ast.parse(text)
            syntax = "python-ast"
            nesting = ast_depth(tree)
        except SyntaxError as exc:
            parse_error = {"line": exc.lineno, "message": exc.msg}

    irreversible = any(item["signal"] == "destructive_write" for item in findings)
    write_signals = sum(item["signal"] in {"destructive_write", "external_write"} for item in findings)

    return {
        "file": str(path),
        "syntax": syntax,
        "lines": len(lines),
        "nesting": nesting,
        "findings": findings,
        "summary": {
            "irreversible_write": irreversible,
            "write_signals": write_signals,
            "signal_count": len(findings),
        },
        "parse_error": parse_error,
    }


def gate(scope: int, blast: int, uncertainty: int, dependency: int, irreversible: bool) -> dict[str, Any]:
    values = {"S": scope, "B": blast, "U": uncertainty, "D": dependency}
    if any(value < 0 or value > 3 for value in values.values()):
        raise ValueError("S/B/U/D must each be in 0..3")

    score = 0.25 * scope + 0.35 * blast + 0.25 * uncertainty + 0.15 * dependency

    # Irreversible writes always force at least the review band. This is a guardrail,
    # not a calibrated probability adjustment.
    if irreversible:
        score = max(score, 1.51)

    if score <= 0.75:
        decision, ceiling = "continue", "patch_leaf"
    elif score <= 1.50:
        decision, ceiling = "probe_then_continue", "patch_local"
    elif score <= 2.25:
        decision, ceiling = "cut_and_review", "patch_leaf"
    else:
        decision, ceiling = "stop_generation", "no_touch"

    if irreversible and decision == "cut_and_review":
        ceiling = "no_touch"

    return {
        "risk_axes": values,
        "heuristic_R": round(score, 3),
        "calibrated_probability": None,
        "irreversible_write": irreversible,
        "decision": decision,
        "max_intervention": ceiling,
        "output_gate": "CUT_OUTPUT" if decision in {"cut_and_review", "stop_generation"} else "OPEN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Endoscope code probe and output gate")
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe", help="Inspect a source file without modifying it")
    p_probe.add_argument("path", type=Path)

    p_gate = sub.add_parser("gate", help="Choose output/intervention ceiling from S/B/U/D")
    p_gate.add_argument("--scope", type=int, required=True, help="S: 0..3")
    p_gate.add_argument("--blast", type=int, required=True, help="B: 0..3")
    p_gate.add_argument("--uncertainty", type=int, required=True, help="U: 0..3")
    p_gate.add_argument("--dependency", type=int, required=True, help="D: 0..3")
    p_gate.add_argument("--irreversible", action="store_true")

    args = parser.parse_args()
    if args.command == "probe":
        result = probe(args.path)
    else:
        result = gate(args.scope, args.blast, args.uncertainty, args.dependency, args.irreversible)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
