# 05 · 验收标准

> 三级验收：**单元（selftest）/ 实例（worked example）/ 回归（字节一致 + 出处核验）**。
> 任一级失败即视为未完成。版本 v1.0 · 2026-11-12

## 5.1 一级：单元测试（必须 3/3）

```bash
python3 scripts/ecr_selftest.py    # 期望输出末行: 结果: 3/3 通过  (exit 0)
```

| 用例 | 断言 | 覆盖算子 |
|---|---|---|
| `t1_layers` | c={x1:2,x2:1,x3:0}；consensus=[x1]；exclusive=[x2]；gap=[x3] 且 `plan.gaps==[x3]` | O1 + 缺口外显（红线 11） |
| `t2_budget_stop` | B=100 → B_U=30；独占证据需 L1=50 → 必须进 `dropped` 且 reason 含"余额不足"；x2 不得被静默注入；`stop_reason` 含 "O4 停机" | O2 + O4（红线 12） |
| `t3_gates_power` | g1(relayed 无出处) 与 g2(usable=false) 拒载且记 failed( B,I / E )；g3 期望格 1.0<5 → 降 undecidable 且 c 不计、进 gaps | O7 + O3 检验力（红线 6/8/9） |

## 5.2 二级：工作实例（必须与下表一致）

```bash
python3 scripts/ecr_plan.py \
  --input refs/worked_example_input.json \
  --root  /mnt/d/hermes_memory/reference/提示词提炼_DEMO_v1_20261111 \
  --out   refs/worked_example_plan.json
```

| 指标 | 期望值（v1.0 实测） |
|---|---|
| status | `ok` |
| 候选池 | 17 个文件 / 125,477 B |
| 预算分池 | B=90,000 ｜ B_L=27,995 ｜ B_U=27,000 ｜ B_C=35,005 |
| 实际注入 | 35,195 B（39.1%） |
| 链长 | 10 步（8 共识 + 1 独占 + 1 锁定） |
| 覆盖 | 共识 [x1,x2,x3] ｜ 独占 [x4,x5] ｜ 缺口 [x6] |
| 门位分布 | `by_gate = {"2": 7, "3": 3}`，`warnings = []` |
| O8 期望格 | `minE=0.045455` / `maxE=1.090909` → `not_applicable_binary` |
| O8 零模型 | C-score 实测 `9.8` vs 保度零分布 `8.9906±0.55034`；`p_low=0.9321`、`p_high=0.1299` |
| verdict | `overall=complete`（预算可行 / 门位 ok / 缺口 1 条属输出） |
| O9 收敛度 | `D=11.5` / `D_max=39.5` / `D_rel=0.291139`，`verdict=first_run` |
| O9 分量 | `gap:1, single_source:2, blocked:0, unverified:0, gate_missing:1, no_corroboration:5, scale_mismatch:1, budget_underuse:1` |
| O9 自比 | 同输入二次运行 `ΔD=0.0`、`verdict=flat`、`monotone=True`（**不得记成 improved**） |
| 升级 | 8 条 L2→L1 |
| 拒载 / 降级 | 0 / 0 |
| 停机 | `O4 停机: 无候选能新增覆盖或提供佐证(边际价值=0)` |

> 若上表任一数字变化而代码已改，必须同步更新本表并在 `CHANGELOG.md` 记原因——**不允许只改代码不改验收表**。

## 5.3 三级：回归

| 项 | 判据 | 实测 |
|---|---|---|
| 确定性 | 同 `--out` 连跑两次，JSON 与 stdout `cmp` 无差异 | ✅ 通过 |
| 出处核验 | `provenance` 中 `bytes_match == false` 的条目数 = 0 | ✅ 17/17 全 match |
| 无随机源 | `grep -n "random\|uuid\|time()"` 于 `ecr_plan.py` → 空 | ✅ |
| 零依赖 | 仅 import `argparse/hashlib/json/os` | ✅ |
| 语法 | `python3 -m py_compile` 两脚本 | ✅ |

## 5.4 未纳入验收的项（明确声明）

1. **语义相关性**：`projections` 由调用方给出，ECR 不验证"这条证据是否真的支持这个子问题"。本实例的 stance 是我人工标注——**这是 ECR 的最大外部依赖，也是它最容易被污染的地方**（若标注者把"看起来像"当"支持"，A 不变量就形同虚设）。
2. **O6 门位**：不再只是告警——`verdict.gate_balance` 输出 `ok|insufficient`。链内含 gate=3 证据而 gate 0/2 全空时判 `insufficient`，`verdict.overall` 随之 `degraded`（`t4 (e)` 断言了 degraded→complete 的翻转）。
3. **`expected_min_cell`**：已由 O8 从边际推导，本实例判 `not_applicable_binary`。0/1 关联矩阵的期望格上限受边际约束（实测 `minE=0.045455`、`maxE=1.090909`，永远够不到 5）→ 逐格推断在该尺度上**无定义**，只能报整体零模型（`p_low=0.9321`、`p_high=0.1299`）。这既不是"数据不足"，也不是待办事项。
4. **多编码者一致性**：输出 `coding` 块（`coders/status/kappa`）。单编码者时显式 `status="single_coder"`、`kappa=null`，并在 `impact` 里声明后果（独占层不得升级为共识）。**不代填 κ**——填它必须真的跑第二编码者。

## 5.5 复现命令（一段可粘贴）

```bash
cd /mnt/d/sanyuan-skills/extensions/evidence-chain-recommendation
python3 -m py_compile scripts/ecr_plan.py scripts/ecr_selftest.py && \
python3 scripts/ecr_selftest.py && \
python3 scripts/ecr_plan.py --input refs/worked_example_input.json \
  --root /mnt/d/hermes_memory/reference/提示词提炼_DEMO_v1_20261111 \
  --out refs/worked_example_plan.json && \
python3 - <<'PY'
import json
d = json.load(open("refs/worked_example_plan.json"))
p = d["provenance"]
print("files:", len(p), "bytes_mismatch:", [k for k, v in p.items() if not v.get("bytes_match")])
print("used:", d["budget"]["total_used"], "/", d["budget"]["B"])
print("gaps:", d["gaps"], "by_gate:", d["coverage"]["by_gate"])
PY
```
