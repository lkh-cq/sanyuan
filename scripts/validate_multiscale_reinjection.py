#!/usr/bin/env python3
"""Deterministic checks for the experimental multiscale reinjection contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"


def main() -> int:
    failures: list[str] = []

    for name in (
        "schema-signal-envelope.schema.json",
        "schema-reinjection-frame.schema.json",
    ):
        try:
            data = json.loads((REFERENCES / name).read_text(encoding="utf-8"))
            if data.get("type") != "object":
                failures.append(f"{name}: root type must be object")
        except Exception as exc:
            failures.append(f"{name}: {exc}")

    try:
        from multiscale_reinjection import (
            Fanout,
            Gate,
            MultiTimescaleReinjection,
            Persistence,
            Propagation,
            Scope,
            SignalEnvelope,
            Source,
            Temporal,
            Timescale,
            utc_now,
        )

        runtime = MultiTimescaleReinjection(reframe_theta=0.5)
        slow = SignalEnvelope(
            signal_id="slow",
            payload_ref="store://slow",
            source=Source(kind="fixture-slow"),
            modality="state",
            temporal=Temporal(utc_now(), Timescale.SLOW, Persistence.PERSISTENT),
            propagation=Propagation(Scope.GLOBAL, Fanout.BROADCAST),
            provenance={"kind": "fixture"},
            task_boundary_ref="bt-test",
            routing_class="slow-to-fast",
        )
        fast = SignalEnvelope(
            signal_id="fast",
            payload_ref="flow://fast",
            source=Source(kind="fixture-fast"),
            modality="runtime-event",
            temporal=Temporal(utc_now(), Timescale.FAST, Persistence.TRANSIENT),
            propagation=Propagation(Scope.LOCAL, Fanout.DENSE),
            provenance={"kind": "fixture"},
            task_boundary_ref="bt-test",
            routing_class="intra-fast",
        )

        changed = runtime.ingest_many([slow, fast])
        if set(changed) != {"slow", "fast"}:
            failures.append("first ingest must emit both deltas")

        converge = runtime.compile_frame(task_boundary_ref="bt-test", changed_ids=changed, rho=0.75)
        if converge.gate is not Gate.CONVERGE:
            failures.append("rho=.75 must stay in CONVERGE for theta threshold .5")
        if abs(converge.rho + converge.theta - 1.0) > 1e-12:
            failures.append("rho + theta must equal 1")

        if runtime.ingest_many([slow]):
            failures.append("unchanged slow signal must not produce a new delta")
        idle = runtime.compile_frame(task_boundary_ref="bt-test", changed_ids=(), rho=0.75)
        if "store://slow" not in idle.persistent_refs:
            failures.append("unchanged persistent slow state must remain addressable")
        if "store://slow" in idle.delta_refs:
            failures.append("unchanged persistent slow state must not be replayed as delta")

        reframe = runtime.compile_frame(
            task_boundary_ref="bt-test",
            changed_ids=(),
            rho=0.25,
            revive_ids=["slow"],
        )
        if reframe.gate is not Gate.REFRAME:
            failures.append("theta=.75 must enter REFRAME for threshold .5")
        if "store://slow" not in reframe.revived_refs:
            failures.append("explicit slow-state revival must be present in REFRAME")
    except Exception as exc:
        failures.append(f"reference runtime: {exc}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: multiscale reinjection contract is structurally consistent")
    print("NOTE: learned routing quality and semantic validity require forward evidence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
