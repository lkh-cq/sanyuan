#!/usr/bin/env python3
"""Deterministic validation for the experimental Endoscope bundle."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"
PROTOCOL = "0.2.0"
PROFILE_PATH = REF / "endoscope-task-profiles.json"
BLOOD_PATH = REF / "endoscope-bloodtesting.yaml"
SCHEMAS = [
    REF / "schema-endoscope-shadow.schema.json",
    REF / "schema-endoscope-event.schema.json",
    REF / "schema-endoscope-gate.schema.json",
    REF / "schema-endoscope-profile.schema.json",
    REF / "schema-endoscope-blood-record.schema.json",
]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    failures: list[str] = []

    try:
        profiles = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        if profiles.get("schema_version") != PROTOCOL:
            fail("task profiles protocol version mismatch", failures)
        profile_map = profiles.get("profiles")
        if not isinstance(profile_map, dict) or not profile_map:
            fail("task profiles must be non-empty", failures)
        else:
            for family, profile in profile_map.items():
                for key in ("protected_functions", "shadow_watch", "trigger_signals", "risk_defaults", "recovery"):
                    if key not in profile:
                        fail(f"profile {family} missing {key}", failures)
    except Exception as exc:
        fail(f"task profiles: {exc}", failures)
        profile_map = {}

    try:
        blood = yaml.safe_load(BLOOD_PATH.read_text(encoding="utf-8"))
        if blood.get("protocol_version") != PROTOCOL:
            fail("Bloodtesting protocol version mismatch", failures)
        cases = blood.get("cases")
        if not isinstance(cases, list) or not cases:
            fail("Bloodtesting cases must be non-empty", failures)
        else:
            ids = [case.get("id") for case in cases]
            if len(ids) != len(set(ids)):
                fail("Bloodtesting case IDs must be unique", failures)
            allowed_e = {"OPEN", "CONTINUE_DIAGNOSTIC", "PAUSE_BEFORE_SIDE_EFFECT", "STOP"}
            allowed_s = {"OPEN", "FILTERED", "QUARANTINED", "DISCARD"}
            allowed_o = {"OPEN", "REVIEW_REQUIRED", "BLOCKED", "REPLACE"}
            for case in cases:
                family = case.get("task_family")
                if family not in profile_map:
                    fail(f"Bloodtesting {case.get('id')} unknown task_family {family}", failures)
                gate = case.get("expected_gate", {})
                if gate.get("execution") not in allowed_e:
                    fail(f"Bloodtesting {case.get('id')} invalid execution gate", failures)
                if gate.get("state") not in allowed_s:
                    fail(f"Bloodtesting {case.get('id')} invalid state gate", failures)
                if gate.get("output") not in allowed_o:
                    fail(f"Bloodtesting {case.get('id')} invalid output gate", failures)
    except Exception as exc:
        fail(f"Bloodtesting: {exc}", failures)

    for schema_path in SCHEMAS:
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                fail(f"{schema_path.name} must declare JSON Schema 2020-12", failures)
        except Exception as exc:
            fail(f"{schema_path.name}: {exc}", failures)

    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "endoscope.py"), "selftest"],
            text=True,
            capture_output=True,
            timeout=30,
        )
        if proc.returncode != 0:
            fail(f"Endoscope selftest failed: {proc.stdout} {proc.stderr}", failures)
        else:
            result = json.loads(proc.stdout)
            if result.get("status") != "PASS":
                fail("Endoscope selftest did not return PASS", failures)
    except Exception as exc:
        fail(f"Endoscope selftest: {exc}", failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        print(f"{len(failures)} Endoscope validation failure(s)")
        return 1

    print("PASS: Endoscope protocol, profiles, fixtures, schemas and Python reference controller")
    print("NOTE: R adapter is validated in a separate CI job with an explicit R runtime")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
