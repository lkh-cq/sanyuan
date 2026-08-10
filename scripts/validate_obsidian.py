#!/usr/bin/env python3
"""Deterministic validation for the experimental Obsidian integration."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "integrations" / "obsidian"
PYTHON_ROOT = INTEGRATION / "python"
PLUGIN = INTEGRATION / "plugin"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    failures: list[str] = []

    try:
        manifest = json.loads((PLUGIN / "manifest.json").read_text(encoding="utf-8"))
        required = {
            "id",
            "name",
            "version",
            "minAppVersion",
            "description",
            "author",
            "isDesktopOnly",
        }
        if set(manifest) != required:
            fail("plugin manifest fields do not match the v1 contract", failures)
        plugin_id = str(manifest.get("id", ""))
        if "obsidian" in plugin_id or plugin_id.endswith("plugin"):
            fail("plugin ID violates Obsidian naming requirements", failures)
        if not manifest.get("isDesktopOnly"):
            fail("plugin must declare desktop-only while it requires a local sidecar", failures)
        package = json.loads((PLUGIN / "package.json").read_text(encoding="utf-8"))
        versions = json.loads((PLUGIN / "versions.json").read_text(encoding="utf-8"))
        if manifest.get("version") != package.get("version"):
            fail("plugin manifest and package versions differ", failures)
        if versions.get(manifest.get("version")) != manifest.get("minAppVersion"):
            fail("versions.json does not map the current minimum app version", failures)
        tracked_build = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "integrations/obsidian/plugin/main.js"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if tracked_build.returncode == 0:
            fail("compiled main.js must be a release asset, not committed source", failures)
    except Exception as exc:
        fail(f"plugin metadata: {exc}", failures)

    try:
        pyproject = tomllib.loads(
            (PYTHON_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        project = pyproject["project"]
        if project.get("dependencies") != []:
            fail("Python v1 runtime must remain zero-dependency", failures)
        if project.get("version") != manifest.get("version"):
            fail("Python and plugin integration versions differ", failures)
    except Exception as exc:
        fail(f"Python package metadata: {exc}", failures)

    try:
        source = (PLUGIN / "src" / "client.ts").read_text(encoding="utf-8")
        if "requestUrl" not in source:
            fail("plugin client must use Obsidian requestUrl", failures)
        if "fetch(" in source or "axios" in source:
            fail("plugin client must not bypass requestUrl", failures)
        settings = (PLUGIN / "src" / "types.ts").read_text(encoding="utf-8")
        if "http://127.0.0.1:8765" not in settings:
            fail("plugin default endpoint must be loopback", failures)
    except Exception as exc:
        fail(f"plugin source policy: {exc}", failures)

    try:
        environment = os.environ.copy()
        source_root = PYTHON_ROOT / "src"
        environment["PYTHONPATH"] = str(source_root) + os.pathsep + environment.get(
            "PYTHONPATH", ""
        )
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(PYTHON_ROOT / "tests"),
                "-v",
            ],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=60,
        )
        if proc.returncode != 0:
            fail(f"Python integration tests failed: {proc.stdout} {proc.stderr}", failures)
    except Exception as exc:
        fail(f"Python integration tests: {exc}", failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        print(f"{len(failures)} Obsidian integration validation failure(s)")
        return 1

    print("PASS: Obsidian sidecar contract, Python tests and plugin metadata")
    print("NOTE: TypeScript compilation runs separately with npm in CI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
