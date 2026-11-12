#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ECR selftest — 三个用例（纯构造数据，不依赖外部路径）。

T1 覆盖分层: 共识 / 独占 / 缺口三层判定 + 缺口必须外显
T2 预算与停机: 池余额不足 → dropped（不得静默注入）+ O4 停机原因
T3 闸门与检验力: 无出处拒载(B/I)、usable 非 true 拒载(E)、期望格<5 降级 undecidable

用法: python3 scripts/ecr_selftest.py     # 全绿 exit 0，任一失败 exit 1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ecr_plan import plan  # noqa: E402


def ev(eid, projs, **kw):
    base = {"id": eid, "path": None, "bytes": kw.pop("bytes", 100),
            "trust_tier": "disk", "gate": 3, "claim_type": "measured",
            "provenance": {"verified": True, "source": "test"}, "proxy_of": None,
            "usable": True, "domain": {"scope": "test", "frozen_scale": "cell_level"},
            "authorization": {"in_scope": True}, "projections": []}
    base.update(kw)
    for sid, stance, l2 in projs:
        base["projections"].append({"subquestion": sid, "stance": stance,
                                    "volume": {"L0": base["bytes"], "L1": l2 * 3, "L2": l2},
                                    "power": {"n": 10, "expected_min_cell": None}})
    return base


def doc(subs, evidence, B=1000, lam=0.30):
    return {"schema": "ecr.task_breakdown/v1", "instance_id": "selftest",
            "task": {"x_id": "x_test", "statement": "",
                     "subquestions": [{"id": s, "text": "", "type": "direction",
                                       "resolution": "free", "critical": True} for s in subs]},
            "budget": {"B": B, "lambda_exclusive": lam}, "evidence": evidence}


CASES = []


def case(fn):
    CASES.append(fn)
    return fn


@case
def t1_layers():
    d = doc(["x1", "x2", "x3"], [ev("e1", [("x1", "support", 10)]),
                                 ev("e2", [("x1", "support", 10)]),
                                 ev("e3", [("x2", "support", 10)])])
    p = plan(d)
    assert p["coverage"]["c"] == {"x1": 2, "x2": 1, "x3": 0}, p["coverage"]["c"]
    assert p["coverage"]["consensus"] == ["x1"], p["coverage"]["consensus"]
    assert p["coverage"]["exclusive"] == ["x2"], p["coverage"]["exclusive"]
    assert p["coverage"]["gap"] == ["x3"], p["coverage"]["gap"]
    assert p["gaps"] == ["x3"], "缺口必须出现在 plan.gaps"
    assert "x1" in p["chain"][0]["subquestions"] or "x2" in p["chain"][0]["subquestions"]
    return "c={x1:2,x2:1,x3:0} layers ok, gap=[x3] 外显"


@case
def t2_budget_stop():
    # B=100 → B_U=30, B_L=0, B_C=70；e3 独占需 L1=50 > B_U → 必须 dropped
    d = doc(["x1", "x2"], [ev("e1", [("x1", "support", 10)]),
                           ev("e2", [("x1", "support", 10)]),
                           ev("e3", [("x2", "support", 16)])], B=100, lam=0.30)
    p = plan(d)
    dropped = {x["evidence"] for x in p["dropped"]}
    assert "e3" in dropped, f"e3 应因 B_U 余额不足被 dropped，实际 {dropped}"
    assert any("余额不足" in x["reason"] for x in p["dropped"])
    assert p["chain"], "至少应注入 x1 的证据"
    assert all("x2" not in s["subquestions"] for s in p["chain"]), "x2 不得被静默注入"
    assert "O4 停机" in p["stop_reason"], p["stop_reason"]
    return f"dropped={sorted(dropped)} 且 x2 未被静默注入"


@case
def t3_gates_power():
    bad_prov = ev("g1", [("x1", "support", 10)], claim_type="relayed",
                  provenance={"verified": False, "source": "hearsay"})
    unusable = ev("g2", [("x2", "support", 10)], usable=False)
    low_power = ev("g3", [("x3", "support", 10)])
    low_power["projections"][0]["power"]["expected_min_cell"] = 1.0
    wrong_bytes = ev("g4", [("x1", "support", 10)], bytes=999)
    d = doc(["x1", "x2", "x3"], [bad_prov, unusable, low_power, wrong_bytes])
    p = plan(d)
    blocked = {x["evidence"] for x in p["blocked"]}
    assert {"g1", "g2"} <= blocked, f"g1(无出处/转述) 与 g2(usable) 应拒载，实际 {blocked}"
    inv = {(x["evidence"], x["invariant"]) for x in p["invariants_failed"]}
    assert ("g1", "B") in inv and ("g1", "I") in inv, inv
    assert ("g2", "E") in inv, inv
    pw = {x["evidence"] for x in p["power_downgraded"]}
    assert "g3" in pw, f"期望格 1.0 < 5 应降级，实际 {pw}"
    assert all(x["to"] == "undecidable" for x in p["power_downgraded"])
    assert p["coverage"]["c"]["x3"] == 0, "降级后不得计入覆盖度"
    assert "x3" in p["gaps"], "降级即缺口，必须外显"
    return f"blocked={sorted(blocked)}, power_downgraded={sorted(pw)}, x3 降级后进 gaps"


def main():
    print("=" * 74)
    print("ECR selftest")
    print("=" * 74)
    fails = 0
    for fn in CASES:
        name = fn.__name__
        try:
            msg = fn()
            print(f"  ✅ {name}: {msg}")
        except AssertionError as e:
            fails += 1
            print(f"  ❌ {name}: {e}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"  ❌ {name}: {type(e).__name__}: {e}")
    print("-" * 74)
    print(f"结果: {len(CASES) - fails}/{len(CASES)} 通过")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
