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
from ecr_o8 import o8_baseline  # noqa: E402


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


@case
def t4_baseline_o8():
    # (a) 稀疏矩阵: 3 证据各覆盖 1 个子问题 → N=3, minE=1/3 → 逐格不可报
    sparse = doc(["s1", "s2", "s3"],
                 [ev("d1", [("s1", "support", 10)]),
                  ev("d2", [("s2", "support", 10)]),
                  ev("d3", [("s3", "support", 10)])])
    a = o8_baseline(sparse, {"d1", "d2", "d3"})
    assert a["matrix"]["N"] == 3, a["matrix"]
    assert a["cell_level"]["status"] == "not_applicable_binary", a["cell_level"]
    assert abs(a["cell_level"]["min_expected"] - 0.333333) < 1e-6, a["cell_level"]
    # 每个列对共享 0 行 → C-score = 1.0；行/列度数全为 1 时交换无法改变矩阵 → 零模型恒定
    assert abs(a["null_model"]["observed"] - 1.0) < 1e-9, a["null_model"]
    assert a["null_model"]["p_low"] == 1.0 and a["null_model"]["p_high"] == 1.0, a["null_model"]
    assert a["null_model"]["null_sd"] == 0.0, "退化零分布必须给出 sd=0，而不是假装有方差"

    # (b) 同输入两次调用必须逐字段一致（固定 seed 的可复现性）
    b = o8_baseline(sparse, {"d1", "d2", "d3"})
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), "O8 非确定性"

    # (c) hub 结构: e00 覆盖全部 10 列, 且 s0 被全部 10 行覆盖 → 单格 maxE=10*10/19≈5.26
    #     用来证明: 即使单格 E 冲到 5 以上, 只要存在小格, 0/1 尺度的逐格推断仍无定义
    ten = [f"s{i}" for i in range(10)]
    hub_ev = [ev("e00", [(s, "support", 10) for s in ten])]
    hub_ev += [ev(f"e{i:02d}", [("s0", "support", 10)]) for i in range(1, 10)]
    dh = doc(ten, hub_ev)
    h = o8_baseline(dh, {e["id"] for e in hub_ev})
    assert h["matrix"]["N"] == 19, h["matrix"]
    assert h["cell_level"]["max_expected"] > 5.0, h["cell_level"]
    assert h["cell_level"]["status"] == "not_applicable_binary", h["cell_level"]

    # (d) counts 尺度下同一矩阵应判 forbidden（说明状态由尺度决定，不是写死的字符串）
    dh2 = dict(dh)
    dh2["matrix_scale"] = "counts"
    h2 = o8_baseline(dh2, {e["id"] for e in hub_ev})
    assert h2["cell_level"]["status"] == "forbidden", h2["cell_level"]

    # (e) 缺口不是"未完成"，但门位孤证是：verdict 必须自报完整度
    p_deg = plan(dh)
    assert p_deg["verdict"]["gate_balance"] == "insufficient", p_deg["verdict"]
    assert p_deg["verdict"]["overall"] == "degraded", p_deg["verdict"]

    dh3 = json.loads(json.dumps(dh))
    for e in dh3["evidence"]:                # 全部改到方法门 → 门位均衡应恢复
        e["gate"] = 2
    p = plan(dh3)
    assert p["verdict"]["cell_level_stats"] == "not_applicable_binary", p["verdict"]
    assert p["verdict"]["gate_balance"] == "ok", p["verdict"]
    assert p["verdict"]["coverage_gaps"] == 0, p["verdict"]
    assert p["verdict"]["overall"] == "complete", p["verdict"]
    return (f"minE={a['cell_level']['min_expected']}(binary 无定义) / hub maxE="
            f"{h['cell_level']['max_expected']} 仍无定义；counts 尺度={h2['cell_level']['status']}；"
            f"零模型 sd={a['null_model']['null_sd']}；两次调用一致")


@case
def t5_convergence_o9():
    from ecr_o9 import score as o9

    poor_doc = doc(["x1", "x2"], [ev("p1", [("x1", "support", 10)], gate=3)])
    poor = plan(poor_doc)

    better_doc = doc(["x1", "x2"], [
        ev("p1", [("x1", "support", 10)], gate=2),
        ev("p2", [("x1", "support", 10)], gate=2),
        ev("p3", [("x2", "support", 10)], gate=2),
        ev("p4", [("x2", "support", 10)], gate=3),
    ])
    better = plan(better_doc, None, 200, poor)

    c = better["convergence"]
    assert c["verdict"] == "improved", c
    assert c["monotone"] is True, c
    assert c["delta"]["D_abs"] < 0, c["delta"]
    assert poor["convergence"]["error_vector"]["gap"] == 1, poor["convergence"]
    assert c["error_vector"]["gap"] == 0, c["error_vector"]

    back = o9(poor, better)
    assert back["verdict"] == "regressed", back
    assert "gap" in back["regressed_by"], back

    flat = o9(better, better)
    assert flat["verdict"] == "flat" and flat["delta"]["D_abs"] == 0, flat

    return (f"D {poor['convergence']['D_abs']} → {c['D_abs']} (Δ{c['delta']['D_abs']})；"
            f"反向={back['verdict']}(上升 {back['regressed_by']})；自比={flat['verdict']}")


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
