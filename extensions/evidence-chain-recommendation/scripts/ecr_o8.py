#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O8 · 基线统计算子 —— 把"现象数据"算出来，不向操作者要判断。

它解决的问题：任何"某子问题证据很多/某类证据被高估"的说法，在扣掉度数边际之前
都不能成立。本模块把边际、准独立期望、调整残差、保度零模型的零分布一次性算平，
输出的是**数值现象**，不是"请人工复核"。

出处（不是自创方法）:
  - 准独立调整残差      Bishop, Fienberg & Holland (1975) Discrete Multivariate Analysis
  - C-score            Stone & Roberts (1990) Oecologia 85:74-79
  - 保度零模型          Gotelli (2000) Ecology 81:2606-2621; Gotelli & Entsminger (2001)
  - 逐格 E<5 不可报       Cochran (1954) 经验规则（渐近卡方近似失效）

刻意保留的"不可判"：
  当 min E < 5 时，本模块**不**给逐格 p 值，而是把 cell_level.status 置为 forbidden
  并给出 min_expected —— 这是数据，不是一个待办事项。
"""

import random

O8_SEED = 20261112
DECIDABLE = ("support", "refute", "partial")


def bipartite(doc, usable):
    """证据 × 子问题 0/1 矩阵（仅计可判定 stance）。"""
    subs = [s["id"] for s in doc["task"]["subquestions"]]
    evs = [ev["id"] for ev in doc["evidence"] if ev["id"] in usable]
    M = {e: {s: 0 for s in subs} for e in evs}
    for ev in doc["evidence"]:
        e = ev["id"]
        if e not in M:
            continue
        for pj in ev.get("projections", []):
            if pj.get("stance") in DECIDABLE and pj.get("subquestion") in M[e]:
                M[e][pj["subquestion"]] = 1
    return subs, evs, M


def c_score(M, evs, subs):
    """Stone & Roberts C-score：列对共享行越少，C 越大（=更分散）。"""
    total, pairs = 0.0, 0
    for j in range(len(subs)):
        Rj = sum(M[e][subs[j]] for e in evs)
        if Rj == 0:
            continue
        for k in range(j + 1, len(subs)):
            Rk = sum(M[e][subs[k]] for e in evs)
            if Rk == 0:
                continue
            shared = sum(1 for e in evs if M[e][subs[j]] and M[e][subs[k]])
            total += (Rj - shared) * (Rk - shared)
            pairs += 1
    return total / pairs if pairs else 0.0


def swap_once(M, evs, subs, rng, attempts):
    """棋盘格交换：同时保住每行/每列出度（双边边际不变）。"""
    n, m = len(evs), len(subs)
    if n < 2 or m < 2:
        return
    for _ in range(attempts):
        i, i2 = rng.randrange(n), rng.randrange(n)
        j, j2 = rng.randrange(m), rng.randrange(m)
        if i == i2 or j == j2:
            continue
        a, b = evs[i], evs[i2]
        s1, s2 = subs[j], subs[j2]
        if M[a][s1] and M[b][s2] and not M[a][s2] and not M[b][s1]:
            M[a][s1] = M[b][s2] = 0
            M[a][s2] = M[b][s1] = 1
        elif M[a][s2] and M[b][s1] and not M[a][s1] and not M[b][s2]:
            M[a][s2] = M[b][s1] = 0
            M[a][s1] = M[b][s2] = 1


def o8_baseline(doc, usable, null_reps=1000):
    subs, evs, M = bipartite(doc, usable)
    rows = {e: sum(M[e].values()) for e in evs}
    cols = {s: sum(M[e][s] for e in evs) for s in subs}
    N = sum(rows.values())

    cells = []
    for e in evs:
        for s in subs:
            if not M[e][s]:
                continue
            E = (rows[e] * cols[s] / N) if N else 0.0
            num = (1 - rows[e] / N) if N else 0.0
            den = (1 - cols[s] / N) if N else 0.0
            z = None
            if E > 0 and num > 0 and den > 0:
                z = (1.0 - E) / ((E * num * den) ** 0.5)
            cells.append({"evidence": e, "subquestion": s, "observed": 1,
                          "expected": round(E, 6),
                          "adj_residual": None if z is None else round(z, 3)})

    minE = min((c["expected"] for c in cells), default=None)
    per_col_minE = {}
    for s in subs:
        vals = [c["expected"] for c in cells if c["subquestion"] == s]
        per_col_minE[s] = min(vals) if vals else None

    obs = c_score(M, evs, subs)
    rng = random.Random(O8_SEED)
    attempts = max(200, 20 * max(1, len(evs)) * max(1, len(subs)))
    null = []
    for _ in range(int(null_reps)):
        W = {e: dict(M[e]) for e in evs}
        swap_once(W, evs, subs, rng, attempts)
        null.append(c_score(W, evs, subs))

    has_null = bool(null)
    mean = sd = p_high = p_low = 0.0
    if has_null:
        mean = sum(null) / len(null)
        sd = (sum((v - mean) ** 2 for v in null) / max(1, len(null) - 1)) ** 0.5
        ge = sum(1 for v in null if v >= obs - 1e-12)
        le = sum(1 for v in null if v <= obs + 1e-12)
        p_high = (ge + 1) / (len(null) + 1)
        p_low = (le + 1) / (len(null) + 1)

    if not has_null:
        null_line = (f"C-score obs={round(obs, 6)}；零分布为空 "
                     f"(n={int(null_reps)}, seed={O8_SEED})")
    else:
        null_line = (f"C-score obs={round(obs, 6)}；零分布 n={int(null_reps)} "
                     f"seed={O8_SEED} mean={round(mean, 6)} sd={round(sd, 6)} "
                     f"p_low={round(p_low, 4)} p_high={round(p_high, 4)}")

    forbidden = (minE is not None and minE < 5.0)
    maxE = max((c["expected"] for c in cells), default=None)
    scale = doc.get("matrix_scale", "binary")
    if forbidden:
        if scale == "counts":
            cell_status = "forbidden"
        else:
            cell_status = "not_applicable_binary"
    else:
        cell_status = "allowed"
    return {
        "operator": "O8",
        "sources": ["Bishop/Fienberg/Holland 1975 (准独立调整残差)",
                    "Stone & Roberts 1990 (C-score)",
                    "Gotelli 2000 (保度零模型)",
                    "Cochran 1954 (逐格 E<5 不可报)"],
        "matrix": {"rows": len(evs), "cols": len(subs), "N": N},
        "margins": {"row": rows, "col": cols},
        "cells": cells,
        "cell_level": {
            "scale": scale,
            "min_expected": minE,
            "max_expected": maxE,
            "threshold": 5.0,
            "status": cell_status,
            "basis": ("0/1 关联矩阵的期望格受边际约束：平衡结构下 E≡1，"
                      "永远达不到 5 → 逐格推断在 binary 尺度上无定义，只能报整体零模型"
                      if cell_status == "not_applicable_binary" else
                      "任一格 E<5 → 渐近近似失效，逐格 p 与逐格 z 一律不报，只报聚合量"),
        },
        "per_subquestion_min_expected": per_col_minE,
        "null_model": {
            "statistic": "C-score (列对共现；棋盘格交换保双边边际)",
            "observed": round(obs, 6),
            "reps": int(null_reps),
            "seed": O8_SEED,
            "swap_attempts_per_rep": attempts,
            "null_mean": round(mean, 6) if has_null else None,
            "null_sd": round(sd, 6) if has_null else None,
            "p_low": round(p_low, 4) if has_null else None,
            "p_high": round(p_high, 4) if has_null else None,
        },
        "readout": [
            f"矩阵 {len(evs)}×{len(subs)}，N={N}",
            "列边际 c: " + ", ".join(f"{s}={cols[s]}" for s in subs),
            "行边际 n_i: " + ", ".join(f"{e}={rows[e]}" for e in evs),
            f"期望格 minE={minE} maxE={maxE}（阈值 5）→ 尺度={scale}，逐格推断={cell_status}",
            null_line,
        ],
    }


if __name__ == "__main__":
    import json
    import sys
    doc = json.load(open(sys.argv[1], encoding="utf-8"))
    usable = {ev["id"] for ev in doc["evidence"]}
    print(json.dumps(o8_baseline(doc, usable), ensure_ascii=False, indent=1))
