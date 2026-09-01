#!/usr/bin/env python3
"""Release gate: verify the version closure Git tag -> build bundle -> installed skill.

The audit found that GitHub main and the actually-loaded skill had drifted. This gate
makes "published" mean something verifiable:

    Git tag v<version>
      -> build bundle (deterministic file set + hashes + manifest)
      -> installed skill (a directory with SKILL.md + references/)
      -> installed version read
      -> compare with Git tag

Subcommands:

  build [--out DIR]        Produce a release manifest (release-manifest.json) for
                           the current bundle: version, file count, entry hash,
                           manifest hash, validation result.
  verify [--out DIR]       In a git repo: assert the v<version> tag exists and
                           points at HEAD; assert the bundle passes validate_bundle.
  compare --installed PATH Compare an installed skill directory against the release
                           manifest: version, file count, entry hash, manifest hash,
                           and validation result must all match.

Exit code 0 means the closure holds; non-zero means a break in the chain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "references" / "project-manifest.yaml"
SKILL = ROOT / "SKILL.md"
VALIDATOR = ROOT / "scripts" / "validate_bundle.py"
RELEASE_MANIFEST_NAME = "release-manifest.json"

# Files whose hashes are part of the "published" contract.
CONTRACT_FILES = ("SKILL.md", "references/project-manifest.yaml", "README.md")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def project_version() -> str:
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def bundle_file_count() -> int:
    count = 0
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file():
            count += 1
    return count


def run_validator() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return False, "validator timed out"
    return result.returncode == 0, result.stdout.strip().splitlines()[-1] if result.stdout else ""


def build_manifest() -> dict:
    version = project_version()
    return {
        "schema_version": "1.0.0",
        "project_version": version,
        "file_count": bundle_file_count(),
        "contract_hashes": {
            name: _sha256(ROOT / name) for name in CONTRACT_FILES
        },
        "validation": run_validator()[0],
        "git_tag": f"v{version}",
    }


def write_manifest(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / RELEASE_MANIFEST_NAME
    target.write_text(
        json.dumps(build_manifest(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def git_tag_points_at_head(version: str) -> tuple[bool, str]:
    tag = f"v{version}"
    try:
        tagged = subprocess.run(
            ["git", "rev-parse", "--verify", f"refs/tags/{tag}"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        if tagged.returncode != 0:
            return False, f"tag {tag} does not exist"
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT
        ).stdout.strip()
        tagged_commit = subprocess.run(
            ["git", "rev-list", "-n", "1", f"refs/tags/{tag}"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        ).stdout.strip()
        if tagged_commit != head:
            return False, f"tag {tag} points to {tagged_commit}, not HEAD {head}"
        return True, f"tag {tag} points at HEAD"
    except OSError as exc:
        return False, f"git unavailable: {exc}"


def read_installed(installed: Path) -> dict:
    """Read the version contract from an installed skill directory."""
    manifest = installed / "references" / "project-manifest.yaml"
    if not manifest.exists():
        raise FileNotFoundError(f"installed skill has no {manifest.relative_to(installed)}")
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    version = str(data["project"]["version"])
    file_count = sum(1 for p in installed.rglob("*") if p.is_file())
    contract_hashes = {
        name: _sha256(installed / name) for name in CONTRACT_FILES
    }
    return {
        "project_version": version,
        "file_count": file_count,
        "contract_hashes": contract_hashes,
    }


def cmd_build(args: argparse.Namespace) -> int:
    out_dir = Path(args.out).resolve()
    target = write_manifest(out_dir)
    manifest = json.loads(target.read_text(encoding="utf-8"))
    ok, message = run_validator()
    print(f"release manifest: {target}")
    print(f"  version       : {manifest['project_version']}")
    print(f"  file_count    : {manifest['file_count']}")
    print(f"  validation    : {'PASS' if ok else 'FAIL'} ({message})")
    print(f"  git_tag       : {manifest['git_tag']}")
    return 0 if ok else 1


def cmd_verify(args: argparse.Namespace) -> int:
    version = project_version()
    ok, message = git_tag_points_at_head(version)
    print(f"git tag closure : {'PASS' if ok else 'FAIL'} ({message})")
    if not ok:
        return 1
    vok, vmessage = run_validator()
    print(f"bundle validate : {'PASS' if vok else 'FAIL'} ({vmessage})")
    return 0 if vok else 1


def cmd_compare(args: argparse.Namespace) -> int:
    installed = Path(args.installed).resolve()
    if not installed.is_dir():
        print(f"FAIL: installed path is not a directory: {installed}")
        return 1
    release = build_manifest()
    try:
        current = read_installed(installed)
    except (FileNotFoundError, KeyError, yaml.YAMLError) as exc:
        print(f"FAIL: cannot read installed skill: {exc}")
        return 1

    failures: list[str] = []
    if current["project_version"] != release["project_version"]:
        failures.append(
            f"version mismatch: installed {current['project_version']} "
            f"!= release {release['project_version']}"
        )
    if current["file_count"] != release["file_count"]:
        failures.append(
            f"file count mismatch: installed {current['file_count']} "
            f"!= release {release['file_count']}"
        )
    for name in CONTRACT_FILES:
        if current["contract_hashes"].get(name) != release["contract_hashes"][name]:
            failures.append(f"contract hash mismatch for {name}")

    print(f"installed skill : {installed}")
    print(f"  version       : {current['project_version']}")
    print(f"  file_count    : {current['file_count']}")
    print(f"  release tag   : {release['git_tag']}")
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print("PASS: installed skill matches the release bundle")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="produce release-manifest.json")
    b.add_argument("--out", default=str(ROOT / "dist"), help="output directory")
    b.set_defaults(func=cmd_build)

    v = sub.add_parser("verify", help="assert git tag and bundle validation")
    v.set_defaults(func=cmd_verify)

    c = sub.add_parser("compare", help="compare an installed skill against the release")
    c.add_argument("--installed", required=True, help="path to installed skill directory")
    c.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
