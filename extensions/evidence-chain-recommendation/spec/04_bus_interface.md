# 04 · 总线接口

> ECR 在 sanyuan 体系里占**注入面**。本文件定义它与其余五个模块的接口契约，以及与 CLI 的调用约定。
> 版本 v1.0 · 2026-11-12

## 4.1 模块关系

```text
原始素材
   │  (1) sanyuan-normalization-port  归一化
   ▼
证据单元 a_i  ──(2) ECR O7 闸门──►  blocked / usable
   │  (3) 藏归（三元）给出 π_i 投影    │
   ▼                                  ▼
命题 x + 分解 x_j ────────► ECR O1..O6 ────────► injection_plan
                                    │
                                    ├─► (4) conscious：注入计划的 ρ 权重提示
                                    └─► (5) sanyuan-router：只接收，不回调
```

| 模块 | ECR 从它取什么 | ECR 给它什么 | 不得越界 |
|---|---|---|---|
| `sanyuan-normalization-port` | 归一化后的 `evidence_unit` | 无（单向） | 不回写归一化结果 |
| 藏归（三元/三题/语法） | 子问题分解 `x₁..x_k` 与 `π_i` 投影 | `gaps`（命题不可证的位置，供三元重标） | 不改写命题 |
| `sanyuan-router` | 无 | 只读的 `injection_plan` | 不产生 PASS/FAIL、不改路由 |
| `conscious` / `consciousness-bus` | `ρ` 收束方向（哪一门/哪一子问题当前是注意力焦点） | `coverage.by_gate`（门位分布，供注意力均衡） | 不算 ρ、不写注意力向量 |
| `unconscious` | 场景边界（何时该归档而非注入） | 无 | 不触发归档动作 |

## 4.2 CLI 契约

```bash
python3 scripts/ecr_plan.py --input <task_breakdown.json> [--root <证据根目录>] [--out <plan.json>]
python3 scripts/ecr_selftest.py
```

| 参数 | 必填 | 语义 |
|---|---|---|
| `--input` | ✅ | `ecr.task_breakdown/v1` 输入（命题 + 子问题 + 候选池） |
| `--root` | 建议 | 证据路径的解析根；给定时**运行时**重算 bytes + sha256 并核对声明值。不给则跳过出处核验（仅限合成用例） |
| `--out` | 可选 | 注入计划落盘路径；不给则只打印 |

**退出码**：`0` 正常（含 `status=infeasible`，那是**结论**不是错误）；`2` 参数/IO 错误；`3` 输入不符合 schema（v1.1 待实现）。

**确定性**：无随机数；同输入 + 同 `--out` 重跑，stdout 与 JSON **字节一致**（已实测）。时间戳一律不写入输出（避免伪差异）。

## 4.3 数据结构契约

三份 JSON，schema 在同目录 `../schema/`：

| 文件 | schema id | 关键字段 |
|---|---|---|
| 输入 | `ecr.task_breakdown/v1` | `task{subquestions[]{id,type,resolution,critical}}`、`budget{B,lambda_exclusive}`、`evidence[]{...}` |
| 证据单元 | `ecr.evidence_unit/v1` | `gate`、`claim_type`、`provenance{verified}`、`proxy_of`、`usable`、`domain{}`、`authorization{}`、`power{}`、`projections[]{subquestion,stance,volume{L0,L1,L2}}` |
| 输出 | `ecr.injection_plan/v1` | `budget{used,residual}`、`coverage{c,consensus,exclusive,gap,by_gate,warnings}`、`chain[]`、`gaps[]`、`dropped[]`、`blocked[]`、`invariants_failed[]`、`power_downgraded[]`、`provenance{}`、`moments{T1..T5}`、`stop_reason` |

**必填留痕位**（缺一即视为未完成）：
`gaps`、`dropped[].reason`、`invariants_failed[]`、`power_downgraded[]`、`provenance[].sha256`、`moments`。

## 4.4 与 Hermes 侧的挂接点

| 挂接点 | 用法 |
|---|---|
| 任务开场 | 用 `moments.T1..T5` 作为落笔前检查表（对应耻辱柱 A–H/I/J 十不变量） |
| 长上下文压缩后 | 用 `gaps` 提醒：缺口不得因压缩而消失（S1-33 族：交接夺舍） |
| 交付前 | 用 `dropped[].reason` 回查被舍弃的证据是否误舍 |
| 归档前 | `provenance` 全量 sha256 作为复现断言（S1-40：补录先溯源） |

## 4.5 已知接口缺口（v1.1 计划）

1. 无 schema 校验器（`jsonschema` 未引入，保持零依赖）→ 计划用 `--strict` 手写最小校验。
2. `expected_min_cell` 需人工填，尚无估计器。
3. 与 `conscious` 的 ρ 字段只是单向输出，尚未形成闭环。
