#!/usr/bin/env python3
"""Reference control-plane prototype for multi-timescale semantic reinjection.

This module is deliberately small. It does not implement embeddings, learned
attention, domain causality, or confidence estimation. It only provides:

- immutable signal routing headers;
- fast/slow state containers;
- delta detection;
- persistent slow-state references without payload replay;
- rho/theta conservation and a configurable reframe gate;
- a minimal ReinjectionFrame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable, Mapping
from uuid import uuid4


class Timescale(str, Enum):
    FAST = "fast"
    INTERMEDIATE = "intermediate"
    SLOW = "slow"
    STATIC = "static"


class Persistence(str, Enum):
    TRANSIENT = "transient"
    SESSION = "session"
    PERSISTENT = "persistent"


class Scope(str, Enum):
    LOCAL = "local"
    REGIONAL = "regional"
    GLOBAL = "global"


class Fanout(str, Enum):
    DENSE = "dense"
    SPARSE = "sparse"
    BROADCAST = "broadcast"


class Gate(str, Enum):
    CONVERGE = "CONVERGE"
    REFRAME = "REFRAME"


@dataclass(frozen=True)
class Source:
    kind: str
    channel: str | None = None
    source_ref: str | None = None


@dataclass(frozen=True)
class Temporal:
    observed_at: str
    timescale: Timescale
    persistence: Persistence
    ttl_ms: int | None = None


@dataclass(frozen=True)
class Propagation:
    scope: Scope
    fanout: Fanout
    hop_limit: int | None = None


@dataclass(frozen=True)
class SignalEnvelope:
    signal_id: str
    payload_ref: str
    source: Source
    modality: str
    temporal: Temporal
    propagation: Propagation
    provenance: Mapping[str, object]
    task_boundary_ref: str
    uncertainty: float | None = None
    routing_class: str | None = None
    dependency_refs: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.signal_id or not self.payload_ref or not self.source.kind:
            raise ValueError("signal_id, payload_ref, and source.kind are required")
        if self.temporal.ttl_ms is not None and self.temporal.ttl_ms < 0:
            raise ValueError("ttl_ms must be non-negative")
        if self.uncertainty is not None and not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("uncertainty must be in [0, 1]")

    @property
    def slow_lane(self) -> bool:
        return self.temporal.timescale in {Timescale.SLOW, Timescale.STATIC}

    def fingerprint(self) -> str:
        """Hash routing-relevant metadata without dereferencing payload content."""
        canonical = {
            "payload_ref": self.payload_ref,
            "source": self.source.__dict__,
            "modality": self.modality,
            "temporal": {
                "observed_at": self.temporal.observed_at,
                "timescale": self.temporal.timescale.value,
                "persistence": self.temporal.persistence.value,
                "ttl_ms": self.temporal.ttl_ms,
            },
            "propagation": {
                "scope": self.propagation.scope.value,
                "fanout": self.propagation.fanout.value,
                "hop_limit": self.propagation.hop_limit,
            },
            "provenance": dict(self.provenance),
            "task_boundary_ref": self.task_boundary_ref,
            "uncertainty": self.uncertainty,
            "routing_class": self.routing_class,
            "dependency_refs": self.dependency_refs,
            "tags": self.tags,
        }
        raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str)
        return sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReinjectionFrame:
    frame_id: str
    task_boundary_ref: str
    delta_refs: tuple[str, ...]
    persistent_refs: tuple[str, ...]
    revived_refs: tuple[str, ...]
    rho: float
    theta: float
    gate: Gate
    active_routes: tuple[str, ...] = ()
    shadow_refs: tuple[str, ...] = ()


@dataclass
class _StoredSignal:
    signal: SignalEnvelope
    fingerprint: str


@dataclass
class ReinjectionState:
    fast: dict[str, _StoredSignal] = field(default_factory=dict)
    slow: dict[str, _StoredSignal] = field(default_factory=dict)

    def ingest(self, signal: SignalEnvelope) -> bool:
        """Store a signal and return True only when it is new or metadata-changed."""
        lane = self.slow if signal.slow_lane else self.fast
        fingerprint = signal.fingerprint()
        previous = lane.get(signal.signal_id)
        changed = previous is None or previous.fingerprint != fingerprint
        lane[signal.signal_id] = _StoredSignal(signal=signal, fingerprint=fingerprint)
        return changed

    def get(self, signal_id: str) -> SignalEnvelope | None:
        item = self.fast.get(signal_id) or self.slow.get(signal_id)
        return item.signal if item else None

    def persistent_payload_refs(self, exclude_ids: set[str] | None = None) -> tuple[str, ...]:
        exclude_ids = exclude_ids or set()
        refs = {
            stored.signal.payload_ref
            for signal_id, stored in self.slow.items()
            if signal_id not in exclude_ids
            and stored.signal.temporal.persistence in {Persistence.SESSION, Persistence.PERSISTENT}
        }
        return tuple(sorted(refs))


class MultiTimescaleReinjection:
    """Metadata router for delta-based context recompilation."""

    def __init__(self, reframe_theta: float = 0.5) -> None:
        if not 0.0 <= reframe_theta <= 1.0:
            raise ValueError("reframe_theta must be in [0, 1]")
        self.reframe_theta = reframe_theta
        self.state = ReinjectionState()

    @staticmethod
    def orient(rho: float) -> tuple[float, float]:
        """Return the conserved control allocation (rho, theta).

        rho must be supplied by an external task policy or observation process;
        this prototype never estimates correctness from model self-report.
        """
        if not 0.0 <= rho <= 1.0:
            raise ValueError("rho must be in [0, 1]")
        theta = 1.0 - rho
        return rho, theta

    def ingest_many(self, signals: Iterable[SignalEnvelope]) -> tuple[str, ...]:
        changed: list[str] = []
        for signal in signals:
            if self.state.ingest(signal):
                changed.append(signal.signal_id)
        return tuple(changed)

    def compile_frame(
        self,
        *,
        task_boundary_ref: str,
        changed_ids: Iterable[str],
        rho: float,
        revive_ids: Iterable[str] = (),
        shadow_refs: Iterable[str] = (),
    ) -> ReinjectionFrame:
        rho, theta = self.orient(rho)
        changed = tuple(dict.fromkeys(changed_ids))
        changed_set = set(changed)
        revived = tuple(dict.fromkeys(revive_ids)) if theta >= self.reframe_theta else ()

        delta_refs: list[str] = []
        active_routes: list[str] = []
        for signal_id in (*changed, *revived):
            signal = self.state.get(signal_id)
            if signal is None:
                continue
            delta_refs.append(signal.payload_ref)
            if signal.routing_class:
                active_routes.append(signal.routing_class)

        return ReinjectionFrame(
            frame_id=f"rf_{uuid4().hex}",
            task_boundary_ref=task_boundary_ref,
            delta_refs=tuple(dict.fromkeys(delta_refs)),
            persistent_refs=self.state.persistent_payload_refs(changed_set | set(revived)),
            revived_refs=tuple(
                self.state.get(signal_id).payload_ref
                for signal_id in revived
                if self.state.get(signal_id) is not None
            ),
            rho=rho,
            theta=theta,
            gate=Gate.REFRAME if theta >= self.reframe_theta else Gate.CONVERGE,
            active_routes=tuple(dict.fromkeys(active_routes)),
            shadow_refs=tuple(dict.fromkeys(shadow_refs)),
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _selftest() -> None:
    runtime = MultiTimescaleReinjection(reframe_theta=0.5)
    slow = SignalEnvelope(
        signal_id="slow-iron-state",
        payload_ref="store://systemic-iron-state",
        source=Source(kind="metabolic"),
        modality="state",
        temporal=Temporal(utc_now(), Timescale.SLOW, Persistence.PERSISTENT),
        propagation=Propagation(Scope.GLOBAL, Fanout.BROADCAST),
        provenance={"kind": "fixture"},
        task_boundary_ref="bt-demo",
        routing_class="slow-to-fast",
    )
    fast = SignalEnvelope(
        signal_id="fast-runtime-event",
        payload_ref="flow://runtime-event-1",
        source=Source(kind="runtime"),
        modality="runtime-event",
        temporal=Temporal(utc_now(), Timescale.FAST, Persistence.TRANSIENT),
        propagation=Propagation(Scope.LOCAL, Fanout.DENSE),
        provenance={"kind": "fixture"},
        task_boundary_ref="bt-demo",
        routing_class="intra-fast",
    )

    changed = runtime.ingest_many([slow, fast])
    frame1 = runtime.compile_frame(task_boundary_ref="bt-demo", changed_ids=changed, rho=0.8)
    assert frame1.gate is Gate.CONVERGE
    assert abs(frame1.rho + frame1.theta - 1.0) < 1e-12
    assert "store://systemic-iron-state" in frame1.delta_refs

    changed_again = runtime.ingest_many([slow])
    assert changed_again == ()
    frame2 = runtime.compile_frame(task_boundary_ref="bt-demo", changed_ids=(), rho=0.8)
    assert "store://systemic-iron-state" in frame2.persistent_refs
    assert "store://systemic-iron-state" not in frame2.delta_refs

    frame3 = runtime.compile_frame(
        task_boundary_ref="bt-demo",
        changed_ids=(),
        rho=0.3,
        revive_ids=["slow-iron-state"],
    )
    assert frame3.gate is Gate.REFRAME
    assert "store://systemic-iron-state" in frame3.revived_refs
    assert "store://systemic-iron-state" in frame3.delta_refs

    print("PASS: multiscale reinjection reference selftest")


if __name__ == "__main__":
    _selftest()
