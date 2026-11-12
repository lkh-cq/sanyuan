#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O9 · 收敛度算子 —— 把"这一轮比上一轮更接近目标"变成一个可算的单调函数。

设计要点（按用户原话）:
  "我要的是它能够对着我们的目标方向, 每掷一次都能更进一步;
   或者说反过来看, 让它离错误目标越来越远, 这样更容易被机器语言这种
   阳性依赖的函数计算到。"

所以这里不度量"对了几分", 而是度量**离错误有多远**:
  D = Σ w_i · e_i        （e_i = 各类错误的计数; 权重正向声明, 不做拟合）
并强制单调性: D_{t+1} ≤ D_t。若上升, 必须点名是哪个分量上升。

权重是**声明**不是调参:
  缺口 3.0 > 单源依赖 2.0 > 拒载 1.5 > 未溯源 1.0 = 门位缺失 1.0
  > 无佐证 0.5 = 尺度不可判 0.5 = 预算低效 0.5

本模块不引入随机数, 给定两个 plan 输出即得唯一结果。
"""

WEIGHTS = {
    "gap": 3.0,              # 子问题 c=0：不可判
    "single_source": 2.0,    # 子问题 c=1：单点依赖
    "blocked": 1.5,          # 被闸门拒载的证据数
    "unverified": 1.0,       # 出处未核（bytes 不符 / provenance 未验证）
    "gate_missing": 1.0,     # 链内 gate 0/2/3 缺几个
    "no_corroboration": 0.5, # 链内每子问题只有 1 条证据
    "scale_mismatch": 0.5,   # 逐格尺度不可判（binary）
    "budget_underuse": 0.5,  # 预算利用率 < 50%
}

COMPONENT_ORDER = ["gap", "single_source", "blocked", "unverified",
                   "gate_missing", "no_corroboration", "scale_mismatch",
                   "budget_underuse"]


def error_vector(plan_out):
    """从 plan 输出读出各类错误计数（全部可回指到具体字段）。"""
    k = len(plan_out["coverage"]["c"])
    cov = plan_out["coverage"]["c"]

    attached = {}
    for st in plan_out["chain"]:
        for s in st.get("subquestions", []):
            attached[s] = attached.get(s, 0) + 1

    prov = plan_out.get("provenance") or {}
    unverified = sum(1 for v in prov.values()
                     if not (isinstance(v, dict) and v.get("exists", False)
                             and v.get("bytes_match", False)))
    by_gate = plan_out["coverage"].get("by_gate") or {}
    gate_missing = sum(1 for g in ("0", "2", "3") if by_gate.get(g, 0) == 0)

    used = plan_out["budget"]["total_used"]
    B = plan_out["budget"]["B"]

    return {
        "gap": len(plan_out["gaps"]),
        "single_source": sum(1 for c in cov.values() if c == 1),
        "blocked": len(plan_out["blocked"]),
        "unverified": unverified,
        "gate_missing": gate_missing,
        "no_corroboration": sum(1 for s in cov if cov[s] > 0 and attached.get(s, 0) <= 1),
        "scale_mismatch": 1 if plan_out["power"]["cell_level_status"] == "not_applicable_binary" else 0,
        "budget_underuse": 1 if (B and used < 0.5 * B) else 0,
    }, k


def d_max(k):
    """理论上界：各项取该任务规模下的最大值，只用一次比例换算。"""
    caps = {
        "gap": k, "single_source": k, "blocked": 1e9, "unverified": 1e9,
        "gate_missing": 3, "no_corroboration": k, "scale_mismatch": 1,
        "budget_underuse": 1,
    }
    caps["blocked"] = 1.0   # blocked 用比例的替代上限，避免规模变化时 D 无故漂移
    caps["unverified"] = 1.0
    return sum(WEIGHTS[c] * caps[c] for c in COMPONENT_ORDER)


def score(plan_out, prev=None):
    ev, k = error_vector(plan_out)
    D = sum(WEIGHTS[c] * ev[c] for c in COMPONENT_ORDER)
    Dm = d_max(k)
    rel = D / Dm if Dm else 0.0

    out = {
        "operator": "O9",
        "objective": "D = Σ w_i·e_i，离错误目标的总距离（越小越好，必须单调不升）",
        "weights": WEIGHTS,
        "error_vector": ev,
        "D_abs": round(D, 4),
        "D_max": round(Dm, 4),
        "D_rel": round(rel, 6),
        "prev": None, "delta": None, "components_delta": None,
        "monotone": None, "verdict": "first_run", "regressed_by": [],
    }

    if prev is None:
        return out

    prev_ev, _ = error_vector(prev)
    prev_D = sum(WEIGHTS[c] * prev_ev[c] for c in COMPONENT_ORDER)
    prev_rel = prev_D / d_max(len(prev["coverage"]["c"]))
    comp_delta = {c: ev[c] - prev_ev[c] for c in COMPONENT_ORDER}
    risers = [c for c in COMPONENT_ORDER if comp_delta[c] > 0]

    out["prev"] = {"D_abs": round(prev_D, 4), "D_rel": round(prev_rel, 6),
                   "error_vector": prev_ev}
    out["delta"] = {"D_abs": round(D - prev_D, 4), "D_rel": round(rel - prev_rel, 6)}
    out["components_delta"] = comp_delta
    out["monotone"] = (D - prev_D) <= 0
    out["regressed_by"] = risers
    if D < prev_D:
        out["verdict"] = "improved"
    elif D == prev_D:
        out["verdict"] = "flat"
    else:
        out["verdict"] = "regressed"
    return out


if __name__ == "__main__":
    import json
    import sys
    a = json.load(open(sys.argv[1], encoding="utf-8"))
    b = json.load(open(sys.argv[2], encoding="utf-8")) if len(sys.argv) > 2 else None
    print(json.dumps(score(a, b), ensure_ascii=False, indent=1))
