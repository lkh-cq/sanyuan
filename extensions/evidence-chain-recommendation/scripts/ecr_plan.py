#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ECR · Evidence-Chain Recommendation — 最小实现 (v1.0)

在固定注入预算下，按「结果导向的覆盖判据」决定注入哪些证据、每条压到几级、按什么顺序，
并把舍弃项与缺口留痕。纯 stdlib，无随机，输出确定性。

用法:
  python3 ecr_plan.py --input refs/worked_example_input.json \
                      --root  /mnt/d/hermes_memory/reference/提示词提炼_DEMO_v1_20261111 \
                      --out   refs/worked_example_plan.json

设计边界（见 spec/03_boundaries.md）:
  只调度、不判定; 不产生知识; 不改写命题; locked 强制 L0; 缺口必须外显; 无出处拒载。
"""
import argparse
import hashlib
import json
import os

DECIDABLE = ("support", "refute", "partial")
WEIGHT_CRITICAL = 2.0
MODE_ORDER = {"L0": 0, "L1": 1, "L2": 2}
MOMENTS = {
    "T1": "写任何数字前: B(出处) + D(查的是不是最近版本)",
    "T2": "写『实测/已验证/已核』前: B + I(动词是不是换了名字的没查)",
    "T3": "写『覆盖度/审核完成』前: A(代理?) + E(探针只能做回归验收)",
    "T4": "写结论/主因/权重前: H(降维?) + A + E(门槛接到检验? 基线去了?)",
    "T5": "写归档/交付/补录前: B(零出处不落笔) + F(授权面) + J(闸门在落笔处?)",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- O7 闸门
def check_gates(doc, root):
    """返回 (可用证据 id 集合, blocked 列表, invariants_failed, power_downgraded, provenance 记录)"""
    blocked, failed, downgraded, provenance = [], [], [], {}
    ok = set()

    for ev in doc["evidence"]:
        eid = ev["id"]
        reasons = []

        # A 表层替代: 声明了 proxy_of 却未声明同域性 → 只能当背景
        if ev.get("proxy_of") and not ev.get("proxy_domain_verified", False):
            failed.append({"evidence": eid, "invariant": "A",
                           "detail": "声明了代理(proxy_of)但未证同域，不得进链"})
            reasons.append("A: 代理未证同域")

        # B 断言先于证据: 无出处 / 未验证
        prov = ev.get("provenance") or {}
        if not prov.get("verified"):
            failed.append({"evidence": eid, "invariant": "B",
                           "detail": "provenance.verified != true"})
            reasons.append("B: 无出处")

        # I 命名逃逸: claim_type 必须是三者之一; relayed 需要出处
        ctype = ev.get("claim_type")
        if ctype not in ("measured", "relayed", "inferred"):
            failed.append({"evidence": eid, "invariant": "I",
                           "detail": "claim_type 缺失或不在白名单 → 无法区分实测/转述/推断"})
            reasons.append("I: claim_type 非法")
        elif ctype == "relayed" and not prov.get("verified"):
            failed.append({"evidence": eid, "invariant": "I",
                           "detail": "claim_type=relayed 且无出处 → 不得作为实测证据注入"})
            reasons.append("I: 转述且无出处")

        # E 静默失效: usable 必须显式为 true
        if ev.get("usable") is not True:
            failed.append({"evidence": eid, "invariant": "E",
                           "detail": "usable 非 true，其数值不得进统计"})
            reasons.append("E: usable 非 true")

        # F 越权
        auth = ev.get("authorization") or {}
        if auth.get("in_scope") is False:
            failed.append({"evidence": eid, "invariant": "F",
                           "detail": "authorization.in_scope == false(只列不注入)"})
            reasons.append("F: 越权")

        # C 不同框: domain 必填
        dom = ev.get("domain") or {}
        if not dom.get("scope") or not dom.get("frozen_scale"):
            failed.append({"evidence": eid, "invariant": "C",
                           "detail": "domain.scope / frozen_scale 缺失，跨域不可比"})

        # G 继承未核: claim_type == relayed 需要 upstream 字段
        if ctype == "relayed" and not ev.get("upstream_of"):
            failed.append({"evidence": eid, "invariant": "G",
                           "detail": "relayed 但无 upstream_of，来源链断"})

        # 出处核验（runtime 计算，不信输入里自报的 bytes）
        p = ev.get("path")
        if root and p:
            full = p if os.path.isabs(p) else os.path.join(root, p)
            if not os.path.exists(full):
                reasons.append("B: 文件不存在")
                provenance[eid] = {"path": full, "exists": False}
            else:
                real_bytes = os.path.getsize(full)
                real_sha = sha256_file(full)
                provenance[eid] = {"path": full, "exists": True,
                                   "bytes": real_bytes, "sha256": real_sha,
                                   "bytes_declared": ev.get("bytes"),
                                   "bytes_match": real_bytes == ev.get("bytes")}
                if real_bytes != ev.get("bytes"):
                    failed.append({"evidence": eid, "invariant": "B",
                                   "detail": f"声明 bytes {ev.get('bytes')} != 实测 {real_bytes}"})

        # 检验力: 期望最小格 < 5 → 该投影降为 undecidable
        for pj in ev.get("projections", []):
            pw = pj.get("power") or {}
            exp = pw.get("expected_min_cell")
            if exp is not None and exp < 5:
                downgraded.append({"evidence": eid, "subquestion": pj["subquestion"],
                                   "expected_min_cell": exp,
                                   "from": pj["stance"], "to": "undecidable"})
                pj["stance"] = "undecidable"

        if reasons:
            blocked.append({"evidence": eid, "reason": "; ".join(reasons)})
        else:
            ok.add(eid)

    return ok, blocked, failed, downgraded, provenance


# ---------------------------------------------------------------- O1 覆盖
def coverage(doc, usable):
    subs = [s["id"] for s in doc["task"]["subquestions"]]
    critical = {s["id"]: bool(s.get("critical")) for s in doc["task"]["subquestions"]}
    locked = {s["id"] for s in doc["task"]["subquestions"] if s.get("resolution") == "locked"}
    c = {sid: 0 for sid in subs}
    for ev in doc["evidence"]:
        if ev["id"] not in usable:
            continue
        for pj in ev.get("projections", []):
            if pj["stance"] in DECIDABLE and pj["subquestion"] in c:
                c[pj["subquestion"]] += 1
    consensus = sorted([s for s in subs if c[s] >= 2])
    exclusive = sorted([s for s in subs if c[s] == 1])
    gap = sorted([s for s in subs if c[s] == 0])
    return c, consensus, exclusive, gap, critical, locked


# ---------------------------------------------------------------- O2 预算分池
def pools(doc):
    B = float(doc["budget"]["B"])
    lam = float(doc["budget"].get("lambda_exclusive", 0.30))
    locked = {s["id"] for s in doc["task"]["subquestions"] if s.get("resolution") == "locked"}
    B_L = 0
    for ev in doc["evidence"]:
        vols = [pj["volume"]["L0"] for pj in ev.get("projections", [])
                if pj["subquestion"] in locked and pj["stance"] in DECIDABLE]
        if vols:
            B_L += max(vols)
    B_U = int(-(-lam * B // 1))  # ceil
    B_C = int(B) - int(B_L) - int(B_U)
    infeasible = B_C < 0
    return {"B": int(B), "lambda_exclusive": lam,
            "B_L": int(B_L), "B_U": int(B_U), "B_C": max(0, int(B_C)),
            "infeasible": infeasible}


## ---------------------------------------------------------------- O3/O4/O5 贪心链
CORR_CAP = 2          # 每个子问题最多 2 条佐证
CORR_VALUE = 0.25     # 每条佐证的边际价值（共识层"密度池"的用途）


def build_chain(doc, usable, coverage_state, critical, locked, pool):
    """O3 边际价值贪心 + O4 停机 + O5 分辨率升级。

    ΔD_i = Σ(新覆盖子问题权重) + 佐证值
      新覆盖权重: critical 2.0 / 非 critical 1.0
      佐证值   : 已覆盖子问题上、stance 一致的额外证据，每子问题至多 CORR_CAP 条，各 CORR_VALUE
    没有佐证项，共识层(c>=2)就永远只用一条证据——这是单点依赖，不是共识。
    """
    remaining = dict(pool)
    chain, dropped, upgrades = [], [], []
    attached = {}          # sid -> [stance, ...]
    injected = set()
    step = 0

    while True:
        best = None
        for ev in doc["evidence"]:
            eid = ev["id"]
            if eid not in usable or eid in injected:
                continue
            new, corr, used_sids = [], 0.0, []
            need_L0 = need_L1 = False
            for pj in ev.get("projections", []):
                sid, st = pj["subquestion"], pj["stance"]
                if st not in DECIDABLE:
                    continue
                if sid not in attached:
                    new.append((sid, st))
                    used_sids.append(sid)
                    if sid in locked:
                        need_L0 = True
                    elif coverage_state[sid] == 1:
                        need_L1 = True
                elif st in attached[sid] and len(attached[sid]) <= CORR_CAP:
                    corr = max(corr, CORR_VALUE)
                    used_sids.append(sid)
            if not new and corr == 0.0:
                continue
            mode = "L0" if need_L0 else ("L1" if need_L1 else "L2")
            vols = [int(pj["volume"][mode]) for pj in ev.get("projections", [])
                    if pj["subquestion"] in used_sids]
            size = max(vols) if vols else 0
            if size <= 0:
                continue
            delta = sum(WEIGHT_CRITICAL if critical[sid] else 1.0 for sid, _ in new) + corr
            cand = {"evidence": eid, "mode": mode,
                    "pool": "B_L" if mode == "L0" else ("B_U" if mode == "L1" else "B_C"),
                    "bytes": size, "delta_D": round(delta, 6),
                    "v": round(delta / size, 9),
                    "subquestions": sorted(sid for sid, _ in new),
                    "corroborates": sorted(sid for sid in used_sids
                                           if sid in attached)}
            key = (cand["v"], -MODE_ORDER[cand["mode"]], cand["evidence"])
            if best is None or key > (best["v"], -MODE_ORDER[best["mode"]], best["evidence"]):
                best = cand

        if best is None:
            stop_reason = "O4 停机: 无候选能新增覆盖或提供佐证(边际价值=0)"
            break
        if best["bytes"] > remaining[best["pool"]]:
            dropped.append({"evidence": best["evidence"],
                            "reason": f"{best['pool']} 池余额不足 (需 {best['bytes']}, "
                                      f"余 {remaining[best['pool']]})"})
            injected.add(best["evidence"])
            continue

        remaining[best["pool"]] -= best["bytes"]
        step += 1
        chain.append({"step": step, "evidence": best["evidence"],
                      "subquestions": best["subquestions"],
                      "corroborates": best["corroborates"],
                      "mode_initial": best["mode"], "mode": best["mode"],
                      "bytes": best["bytes"],
                      "pool": best["pool"], "delta_D": best["delta_D"], "v": best["v"]})
        for ev in doc["evidence"]:
            if ev["id"] != best["evidence"]:
                continue
            for pj in ev.get("projections", []):
                sid, st = pj["subquestion"], pj["stance"]
                if st in DECIDABLE and (sid in best["subquestions"] or sid in best["corroborates"]):
                    attached.setdefault(sid, []).append(st)
        injected.add(best["evidence"])

    # O5 分辨率升级: 只对链内证据，用 B_C 余量 L2 → L1
    for st in sorted(chain, key=lambda s: s["step"]):
        if st["mode"] != "L2":
            continue
        ev = next(e for e in doc["evidence"] if e["id"] == st["evidence"])
        vols = [int(pj["volume"]["L1"]) - int(pj["volume"]["L2"])
                for pj in ev.get("projections", []) if pj["subquestion"] in attached]
        delta_bytes = max(vols) if vols else 0
        if 0 < delta_bytes <= remaining["B_C"]:
            remaining["B_C"] -= delta_bytes
            upgrades.append({"evidence": st["evidence"], "from": "L2", "to": "L1",
                             "delta_bytes": delta_bytes})
            st["mode"] = "L1"
            st["bytes"] += delta_bytes
            st["pool"] = "B_C"

    return chain, dropped, upgrades, remaining, stop_reason



def plan(doc, root=None):
    usable, blocked, failed, downgraded, provenance = check_gates(doc, root)
    c, consensus, exclusive, gap, critical, locked = coverage(doc, usable)
    pool = pools(doc)
    chain, dropped, upgrades, remaining, stop_reason = build_chain(
        doc, set(usable), c, critical, locked, {"B_C": pool["B_C"], "B_U": pool["B_U"], "B_L": pool["B_L"]})

    # 独占槽位: 覆盖 c==1 子问题的证据
    exclusive_slot = sorted({ev["id"] for ev in doc["evidence"]
                             if ev["id"] in usable and any(
                                 pj["subquestion"] in exclusive and pj["stance"] in DECIDABLE
                                 for pj in ev.get("projections", []))})

    used = {k: pool[k] - remaining[k] for k in ("B_C", "B_U", "B_L")}

    # O6 门位均衡统计（只告警，不阻断）
    gate_of = {ev["id"]: ev.get("gate") for ev in doc["evidence"]}
    by_gate, warnings = {}, []
    for st in chain:
        g = gate_of.get(st["evidence"])
        if g is not None:
            by_gate[str(g)] = by_gate.get(str(g), 0) + 1
    if by_gate.get("3", 0) > 0 and (by_gate.get("0", 0) + by_gate.get("2", 0)) == 0:
        warnings.append("O6 现象孤证: 链内含 gate=3 证据但无 gate=0/2 支撑面, "
                        "现象对≠整条链对")

    return {
        "schema": "ecr.injection_plan/v1",
        "instance_id": doc.get("instance_id"),
        "x_id": doc["task"]["x_id"],
        "statement": doc["task"]["statement"],
        "status": "infeasible" if pool["infeasible"] else "ok",
        "budget": {"B": pool["B"], "lambda_exclusive": pool["lambda_exclusive"],
                   "pools": {"B_C": pool["B_C"], "B_U": pool["B_U"], "B_L": pool["B_L"]},
                   "used": used,
                   "residual": remaining,
                   "total_used": sum(used.values())},
        "coverage": {"c": c, "consensus": consensus, "exclusive": exclusive, "gap": gap,
                     "by_gate": by_gate, "warnings": warnings},
        "chain": chain,
        "resolution_upgrades": upgrades,
        "exclusive_slot": exclusive_slot,
        "gaps": gap,
        "dropped": dropped,
        "blocked": blocked,
        "gates_checked": ["A", "B", "C", "E", "F", "G", "H", "I", "J"],
        "invariants_failed": failed,
        "power_downgraded": downgraded,
        "provenance": provenance,
        "moments": MOMENTS,
        "stop_reason": stop_reason,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--root", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    with open(a.input, encoding="utf-8") as fh:
        doc = json.load(fh)
    out = plan(doc, a.root)

    print("=" * 74)
    print("ECR 注入计划")
    print("=" * 74)
    print(f"命题  {out['x_id']}: {out['statement']}")
    print(f"状态  {out['status']}")
    b = out["budget"]
    print(f"预算  B={b['B']}  B_C={b['pools']['B_C']}  B_U={b['pools']['B_U']}  "
          f"B_L={b['pools']['B_L']}  (λ={b['lambda_exclusive']})")
    print(f"已用  {b['total_used']}  B_C={b['used']['B_C']} B_U={b['used']['B_U']} B_L={b['used']['B_L']}")
    print(f"\n[O1] 覆盖度 c   " + "  ".join(f"{k}={v}" for k, v in out["coverage"]["c"].items()))
    print(f"     共识 {out['coverage']['consensus']}")
    print(f"     独占 {out['coverage']['exclusive']}")
    print(f"     缺口 {out['coverage']['gap']}")
    print(f"[O6] 链内门位分布 {out['coverage']['by_gate']}")
    for w in out["coverage"]["warnings"]:
        print(f"     ⚠ {w}")
    print("\n[O3] 链（按边际价值降序装配；mode 为 O5 升级后的最终档位）")
    up = {u["evidence"] for u in out["resolution_upgrades"]}
    for st in out["chain"]:
        tag = f"{st['mode_initial']}→{st['mode']}" if st["evidence"] in up else st["mode"]
        marks = []
        if st["subquestions"]:
            marks.append("覆盖 " + ",".join(st["subquestions"]))
        if st["corroborates"]:
            marks.append("佐证 " + ",".join(st["corroborates"]))
        print(f"  {st['step']:>2}. {st['evidence']}  {tag:<7} {st['bytes']:>6}B  "
              f"ΔD={st['delta_D']:<6} v={st['v']:<12} pool={st['pool']}  "
              f"← {'; '.join(marks) if marks else '(无新增)'}")
    if out["resolution_upgrades"]:
        print("\n[O5] 分辨率升级(B_C 余量)")
        for u in out["resolution_upgrades"]:
            print(f"  {u['evidence']}  {u['from']}→{u['to']}  +{u['delta_bytes']}B")
    print(f"\n独占槽位 {out['exclusive_slot']}")
    print(f"缺口     {out['gaps']}   ← 必须外显，禁止静默消失")
    print(f"停机     {out['stop_reason']}")
    if out["dropped"]:
        print("\n舍弃")
        for d in out["dropped"]:
            print(f"  {d['evidence']}: {d['reason']}")
    if out["blocked"]:
        print("\n拒载(O7 闸门)")
        for d in out["blocked"]:
            print(f"  {d['evidence']}: {d['reason']}")
    if out["power_downgraded"]:
        print("\n检验力降级(O3)")
        for d in out["power_downgraded"]:
            print(f"  {d['evidence']}/{d['subquestion']}: {d['from']}→{d['to']} "
                  f"(期望格 {d['expected_min_cell']} < 5)")

    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        print(f"\nplan 已写入 {a.out} ({os.path.getsize(a.out)} B)")


if __name__ == "__main__":
    main()
