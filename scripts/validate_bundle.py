#!/usr/bin/env python3
"""Validate deterministic structure for the installable consciousness-bus bundle.

This script deliberately does not claim semantic understanding. Frozen meanings,
front-end behavior, and downstream RAG quality require review plus independent
forward tests.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterator

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
MANIFEST = ROOT / "references" / "project-manifest.yaml"
ACCEPTANCE = ROOT / "references" / "acceptance-tests.yaml"
FRONTEND_ACCEPTANCE = ROOT / "references" / "frontend-acceptance-tests.yaml"
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
REPO_PATH_PREFIXES = ("references/", "assets/", "scripts/", ".github/")


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


def walk(value: object) -> Iterator[object]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def manifest_paths(manifest: dict) -> set[str]:
    paths: set[str] = set()
    for value in walk(manifest):
        if not isinstance(value, str):
            continue
        if value == "SKILL.md" or value.startswith(REPO_PATH_PREFIXES):
            paths.add(value.split("#", 1)[0])
    return paths


def registered_modules(manifest: dict) -> dict[str, dict]:
    modules: dict[str, dict] = {}
    for value in walk(manifest):
        if not isinstance(value, dict) or "module_id" not in value:
            continue
        module_id = value["module_id"]
        if not isinstance(module_id, str):
            raise ValueError("module_id must be a string")
        if module_id in modules:
            raise ValueError(f"duplicate module_id: {module_id}")
        modules[module_id] = value
    return modules


def check_markdown_links(failures: list[str]) -> None:
    markdown_files = [SKILL, ROOT / "README.md", ROOT / "CONTRIBUTING.md"]
    markdown_files.extend(sorted((ROOT / "references").glob("*.md")))
    for path in markdown_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in link or link.startswith("#"):
                continue
            relative = link.split("#", 1)[0]
            target = (path.parent / relative).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                fail(f"link escapes repository: {path.relative_to(ROOT)} -> {link}", failures)
                continue
            if not target.exists():
                fail(f"broken link: {path.relative_to(ROOT)} -> {link}", failures)


def check_recipe(failures: list[str]) -> None:
    try:
        recipe = yaml.safe_load(
            (ROOT / "references" / "research-recipe.yaml").read_text(encoding="utf-8")
        )
        sequence = recipe["sequence"]
        numbers = [item["step"] for item in sequence]
        if numbers != sorted(numbers) or len(numbers) != len(set(numbers)):
            fail("research recipe steps must be unique and ascending", failures)

        steps = {item.get("module"): item["step"] for item in sequence if "module" in item}
        boundary = steps["task-boundary-compiler"]
        if not boundary < steps["meta-normalization"]:
            fail("task boundary must precede meta normalization", failures)
        if not boundary < steps["hu-normalization"]:
            fail("task boundary must precede hu normalization", failures)

        frame_steps = [
            item["step"]
            for item in sequence
            if "RAGRequestFrame" in str(item.get("action", ""))
            or "RAGRequestFrame" in str(item.get("output", ""))
        ]
        if not frame_steps:
            fail("research recipe must terminate in RAGRequestFrame compilation", failures)
        elif max(numbers) != max(frame_steps):
            fail("RAGRequestFrame compilation must be the final research front-end step", failures)

        modules = set(recipe.get("modules", []))
        if "reader-facing-analysis" in modules:
            fail("reader-facing-analysis must not be in the front-end core recipe", failures)
    except Exception as exc:
        fail(f"research recipe: {exc}", failures)


def _check_case_file(path: Path, required_keys: tuple[str, ...], failures: list[str]) -> None:
    try:
        acceptance = yaml.safe_load(path.read_text(encoding="utf-8"))
        cases = acceptance.get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError("cases must be a non-empty list")
        ids: list[str] = []
        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                raise ValueError(f"case {index} must be a mapping")
            for key in required_keys:
                if key not in case:
                    raise ValueError(f"case {index} missing {key}")
            if not isinstance(case["id"], str) or not case["id"]:
                raise ValueError(f"case {index} has invalid id")
            if not isinstance(case["must"], list) or not isinstance(case["must_not"], list):
                raise ValueError(f"case {case['id']} must use list assertions")
            ids.append(case["id"])
        if len(ids) != len(set(ids)):
            fail(f"{path.name} case IDs must be unique", failures)
    except Exception as exc:
        fail(f"{path.name}: {exc}", failures)


def check_acceptance(failures: list[str]) -> None:
    _check_case_file(
        ACCEPTANCE,
        ("id", "prompt", "expected_mode", "must", "must_not"),
        failures,
    )
    _check_case_file(
        FRONTEND_ACCEPTANCE,
        ("id", "prompt", "initial_filter_state", "must", "must_not"),
        failures,
    )


def main() -> int:
    failures: list[str] = []
    repository_context = (ROOT / ".git").exists() or (ROOT / "README.md").exists()

    try:
        skill_text = SKILL.read_text(encoding="utf-8")
        metadata = frontmatter(skill_text)
        if set(metadata) != {"name", "description"}:
            fail("SKILL.md frontmatter must contain only name and description", failures)
        if metadata.get("name") != "consciousness-bus":
            fail("unexpected skill name", failures)
    except Exception as exc:
        fail(f"SKILL.md: {exc}", failures)

    try:
        architecture = frontmatter(
            (ROOT / "references" / "architecture.md").read_text(encoding="utf-8")
        )
        if architecture.get("authority") != "frozen-ontology":
            fail("architecture must declare frozen-ontology authority", failures)
    except Exception as exc:
        fail(f"architecture: {exc}", failures)

    try:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest must be a mapping")
        project_version = str(manifest["project"]["version"])
        if not SEMVER.fullmatch(project_version):
            fail("project.version must use semantic versioning", failures)

        paths = manifest_paths(manifest)
        for relative in sorted(paths):
            if relative.startswith("reference/"):
                continue
            if relative.startswith(".github/") and not repository_context:
                continue
            if not (ROOT / relative).exists():
                fail(f"missing manifest path: {relative}", failures)

        reference_files = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "references").iterdir()
            if path.is_file()
        }
        unregistered = sorted(reference_files - paths)
        if unregistered:
            fail(f"unregistered reference files: {unregistered}", failures)

        modules = registered_modules(manifest)
        for module_id, module in modules.items():
            if "version" in module and not SEMVER.fullmatch(str(module["version"])):
                fail(f"module {module_id} has non-semver version", failures)

        lifecycle = manifest.get("module_lifecycle", {})
        assigned: dict[str, str] = {}
        for status, module_ids in lifecycle.items():
            if status not in manifest.get("lifecycle_definitions", {}):
                fail(f"undefined lifecycle status: {status}", failures)
            if not isinstance(module_ids, list):
                fail(f"lifecycle {status} must be a list", failures)
                continue
            for module_id in module_ids:
                if module_id in assigned:
                    fail(f"module {module_id} appears in multiple lifecycles", failures)
                assigned[module_id] = status
        missing_lifecycle = sorted(set(modules) - set(assigned))
        unknown_lifecycle = sorted(set(assigned) - set(modules))
        if missing_lifecycle:
            fail(f"modules missing lifecycle: {missing_lifecycle}", failures)
        if unknown_lifecycle:
            fail(f"lifecycle lists unknown modules: {unknown_lifecycle}", failures)

        allowed_version_duplicates = {MANIFEST, ROOT / "references" / "version-provenance.md"}
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or path in allowed_version_duplicates:
                continue
            if path.suffix.lower() not in {".md", ".yaml", ".yml", ".py"}:
                continue
            if project_version in path.read_text(encoding="utf-8"):
                fail(
                    f"project version duplicated outside manifest/provenance: {path.relative_to(ROOT)}",
                    failures,
                )
    except Exception as exc:
        fail(f"project manifest: {exc}", failures)

    check_markdown_links(failures)
    check_recipe(failures)
    check_acceptance(failures)

    for yaml_path in sorted((ROOT / "references").glob("*.yaml")):
        try:
            yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"invalid YAML {yaml_path.name}: {exc}", failures)

    try:
        agent = yaml.safe_load((ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        if not set(agent).issubset({"interface", "dependencies", "policy"}):
            fail("agents/openai.yaml has unsupported top-level fields", failures)
        if repository_context and "products" in agent.get("policy", {}):
            fail("agents/openai.yaml must not claim unverified products", failures)
        default_prompt = agent.get("interface", {}).get("default_prompt", "")
        if "$consciousness-bus" not in default_prompt:
            fail("default_prompt must mention $consciousness-bus", failures)
    except Exception as exc:
        fail(f"agents/openai.yaml: {exc}", failures)

    for canvas in sorted((ROOT / "assets" / "canvas").glob("*.canvas")):
        try:
            data = json.loads(canvas.read_text(encoding="utf-8"))
            for node in data.get("nodes", []):
                relative = node.get("file")
                if relative and not (ROOT / relative).exists():
                    fail(f"{canvas.name} has broken file node: {relative}", failures)
        except Exception as exc:
            fail(f"invalid Canvas {canvas.name}: {exc}", failures)

    if repository_context:
        for required in (
            "LICENSE",
            "README.md",
            "CONTRIBUTING.md",
            ".github/workflows/validate.yml",
        ):
            if not (ROOT / required).exists():
                fail(f"missing repository file: {required}", failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        print(f"{len(failures)} validation failure(s)")
        return 1

    print("PASS: deterministic bundle structure is internally consistent")
    print("NOTE: semantic invariants require review and independent forward tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
