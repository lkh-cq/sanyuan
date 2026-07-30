#!/usr/bin/env python3
"""Validate the installable consciousness-bus skill bundle."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
MANIFEST = ROOT / "references" / "project-manifest.yaml"
ACCEPTANCE = ROOT / "references" / "acceptance-tests.yaml"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def frontmatter(text: str) -> dict:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("missing YAML frontmatter")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("frontmatter must be a mapping")
    return value


def iter_paths(value: object, parent_key: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_paths(child, str(key))
    elif isinstance(value, list):
        for child in value:
            yield from iter_paths(child, parent_key)
    elif isinstance(value, str) and parent_key in {
        "root",
        "research",
        "fast_filter",
        "path",
        "entrypoint",
        "encoder",
        "normalizer",
        "total",
        "sancai",
        "santi",
        "flow",
        "meta_hu",
        "provenance",
    }:
        yield value


def main() -> int:
    failures: list[str] = []

    try:
        skill_text = SKILL.read_text(encoding="utf-8")
        metadata = frontmatter(skill_text)
        if set(metadata) != {"name", "description"}:
            fail("SKILL.md frontmatter must contain only name and description", failures)
        if metadata.get("name") != "consciousness-bus":
            fail("unexpected skill name", failures)
    except Exception as exc:
        fail(f"SKILL.md: {exc}", failures)
        skill_text = ""

    for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", skill_text):
        if "://" in link or link.startswith("#"):
            continue
        if not (ROOT / link).exists():
            fail(f"broken SKILL.md link: {link}", failures)

    try:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        if manifest["project"]["version"] != "3.2.0":
            fail("manifest project version must be 3.2.0", failures)
        for relative in iter_paths(manifest):
            if relative.startswith("reference/"):
                continue
            if not (ROOT / relative).exists():
                fail(f"missing manifest path: {relative}", failures)
    except Exception as exc:
        fail(f"project manifest: {exc}", failures)

    required_invariants = {
        "architecture.md": [
            "天才 = 规律",
            "地才 = 环境",
            "人才 = 实践",
            "天题 = 信息的本来样貌",
            "地题 = 读取方式",
            "人题 = 读取记录",
            "FlowEvent ⊂ 互",
            "ρ+θ=1",
            "调用时O(1)查表",
            "不另设“天元/地元/人元”分类",
        ],
        "task-boundary.md": ["B_T", "F_T", "forbidden_loss", "epsilon_T"],
        "hu-observation-space.md": ["互 ≠ 信息论中的 mutual information", "FlowEvent ⊂ 互"],
        "n-focus.md": ["offline", "O(1)"],
    }
    for filename, needles in required_invariants.items():
        text = (ROOT / "references" / filename).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                fail(f"{filename} missing invariant: {needle}", failures)

    forbidden_active = {
        "architecture.md": ["三思而后行 -> 多重归一化过滤", "> 版本: 3.1.0"],
        "task-boundary.md": ["预处理/多重归一化过滤/SKILL.md"],
    }
    for filename, needles in forbidden_active.items():
        text = (ROOT / "references" / filename).read_text(encoding="utf-8")
        for needle in needles:
            if needle in text:
                fail(f"{filename} retains obsolete active text: {needle}", failures)

    try:
        recipe = yaml.safe_load(
            (ROOT / "references" / "research-recipe.yaml").read_text(encoding="utf-8")
        )
        steps = {item.get("module"): item["step"] for item in recipe["sequence"] if "module" in item}
        if not (
            steps["task-boundary-compiler"]
            < steps["meta-normalization"]
            and steps["task-boundary-compiler"] < steps["hu-normalization"]
        ):
            fail("task boundary must precede both normalizers", failures)
    except Exception as exc:
        fail(f"research recipe: {exc}", failures)

    try:
        acceptance = yaml.safe_load(ACCEPTANCE.read_text(encoding="utf-8"))
        cases = acceptance.get("cases", [])
        if len(cases) < 6:
            fail("acceptance suite must contain at least six cases", failures)
        if len({case["id"] for case in cases}) != len(cases):
            fail("acceptance case IDs must be unique", failures)
    except Exception as exc:
        fail(f"acceptance tests: {exc}", failures)

    for schema in sorted((ROOT / "references").glob("*.yaml")):
        try:
            yaml.safe_load(schema.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"invalid YAML {schema.name}: {exc}", failures)

    for canvas in sorted((ROOT / "assets" / "canvas").glob("*.canvas")):
        try:
            data = json.loads(canvas.read_text(encoding="utf-8"))
            for node in data.get("nodes", []):
                relative = node.get("file")
                if relative and not (ROOT / relative).exists():
                    fail(f"{canvas.name} has broken file node: {relative}", failures)
        except Exception as exc:
            fail(f"invalid Canvas {canvas.name}: {exc}", failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        print(f"{len(failures)} validation failure(s)")
        return 1

    print("PASS: consciousness-bus bundle is internally consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
