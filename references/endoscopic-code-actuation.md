---
name: Endoscopic Code Actuation
module_id: extension-endoscopic-code-actuation
description: "面向代码生成与修改任务的实验性风险感知干预层。通过 Endoscope 探针定位高危状态，Bloodtesting 校准易出血位置，并分别控制执行、中间状态与最终输出。"
version: 0.1.1
category: extension
manifest_ref: references/project-manifest.yaml
---

# Endoscopic Code Actuation

> 这是实验性扩展，不改变冻结本体。它不是通用 Agent，也不声称能在线修改模型权重。
> 它把“继续生成完整代码”降级为一种可被中断的动作，把“探测—审核—局部干预—验证”提升为代码任务中的默认高风险路径。

## 1. 核心定义

Endoscope 同时包含四类能力：

1. **观察**：读取最小必要代码结构、运行时状态、类型、依赖与错误信号；
2. **干预**：在允许层级内执行局部替换、删除、参数收紧、回滚或停止写入；
3. **状态隔离**：允许计算继续，但把可疑中间结果标记为 tainted/quarantined，不直接注入最终解释；
4. **输出闸门**：当风险信号已足够确定时，阻断最终交付或停止继续展开源码，把控制权交给审核与验证。

目标不是“让 LLM 更快吐完整代码”，而是尽量避免完整代码和未经审核的计算结果成为模型与环境之间的默认通信介质。

```text
LLM 意图 -> Probe -> Risk locus -> Gate(E/S/O) -> Review -> Actuate/Do-not-touch -> Verify -> Release/Commit/Rollback
```

## 2. 三闸门：执行、状态、输出必须分离

`CUT_OUTPUT` 不再等价于 `STOP_EXECUTION`。Endoscope 使用三个独立控制面：

```text
E = Execution Gate
    OPEN | CONTINUE_DIAGNOSTIC | PAUSE_BEFORE_SIDE_EFFECT | STOP

S = State Gate
    OPEN | FILTERED | QUARANTINED

O = Output Gate
    OPEN | BLOCKED | RELEASED
```

典型情形：统计模型已经运行成功，但变量解释受到强共线性污染。

```text
E = OPEN
S = QUARANTINED
O = BLOCKED
```

此时可以继续 bootstrap、交叉验证、残差分析或稳定性选择来收集证据，但禁止把未经审核的解释作为最终结论返回。

只有当运算本身将触发不可逆副作用（删除、生产写入、权限修改、迁移等）时，才把 `E` 提升为 `PAUSE_BEFORE_SIDE_EFFECT` 或 `STOP`。

## 3. 最小协议

控制器只需要识别以下动作：

```text
PROBE                读取局部状态，不修改
CONTINUE_DIAGNOSTIC  继续安全的诊断性计算
QUARANTINE_STATE     隔离可疑中间结果
CUT_OUTPUT            停止继续生成源码或阻断未经审核的最终输出
REVIEW                审核当前节点、依赖与影响范围
PATCH_LEAF            只改叶节点或单一表达式
PATCH_LOCAL           允许单函数/单模块局部修改
RELEASE_OUTPUT        审核通过后开放最终交付
ROLLBACK              回到上一个稳定检查点
COMMIT                验证通过后提交
NO_TOUCH              禁止自动修改，只允许观察与建议
```

推荐机器接口使用短 JSON：

```json
{"op":"probe","target":"symbol://score/calc","need":["signature","callers","writes"]}
```

发现解释层“出血”但计算仍安全时：

```json
{"execution_gate":"OPEN","state_gate":"QUARANTINED","output_gate":"BLOCKED","next":"CONTINUE_DIAGNOSTIC"}
```

发现不可逆写入时：

```json
{"execution_gate":"PAUSE_BEFORE_SIDE_EFFECT","state_gate":"QUARANTINED","output_gate":"BLOCKED","next":"REVIEW"}
```

这允许流式控制器只截断真正不该继续的通道，而不是把计算、状态和交付粗暴地绑成一个开关。

## 4. Bloodtesting：用“出血点”训练警惕心

Bloodtesting 不是把错误样本直接蒸馏成“标准答案”，而是记录 **LLM 在何处最早应该停下来探测，以及应该关哪一个闸门**。

每个样本做成一组对照：

- **A 组：continue-generation** — 允许模型按原习惯继续写，记录首次错误、错误扩散范围与多余输出；
- **B 组：probe-gate-review** — 在候选高危点触发 Endoscope，记录首次探针、E/S/O 三闸门状态、是否避免错误传播；
- 比较指标：`first_bleed_locus`、`propagation_span`、`avoidable_output_tokens`、`false_alarm`、`missed_bleed`、`repair_scope`、`gate_accuracy`。

仓库内置 10 组初始嵌套复合代码样本：[`endoscope-bloodtesting.yaml`](endoscope-bloodtesting.yaml)。这些样本只用于校准控制策略，不构成任何模型能力证明。

## 5. 风险不是单一“代码长度”

Endoscope 把风险拆成四个轴：

- `S`：scope，修改范围；
- `B`：blast radius，执行或写入后的影响半径；
- `U`：uncertainty，模型对当前状态的不确定性；
- `D`：dependency depth，依赖链深度。

初始启发式：

```text
R = 0.25*S + 0.35*B + 0.25*U + 0.15*D
```

四个轴均取 0..3。该公式只是 **未校准初始权重**，后续应由 Bloodtesting 实测调整；禁止把它解释成真实错误概率。

### 风险层级与默认闸门

| R 区间 | E：执行 | S：状态 | O：输出 | 允许的最高干预 |
| --- | --- | --- | --- | --- |
| 0.00–0.75 | `OPEN` | `OPEN` | `OPEN` | `PATCH_LEAF` |
| >0.75–1.50 | `OPEN` | `FILTERED` | `OPEN` | `PATCH_LOCAL` |
| >1.50–2.25 | `CONTINUE_DIAGNOSTIC` | `QUARANTINED` | `BLOCKED` | 明确定位后的 `PATCH_LEAF` |
| >2.25 | `CONTINUE_DIAGNOSTIC` | `QUARANTINED` | `BLOCKED` | `NO_TOUCH` |

如果存在不可逆外部写入、删除、数据库迁移、基础设施变更、密钥/权限变更或跨仓库大范围重构，即使代码行数很少，`E` 也至少提升为 `PAUSE_BEFORE_SIDE_EFFECT`，且 `O=BLOCKED`。

## 6. “什么能碰，什么不能碰”

### 叶级：可碰

- 单一纯函数表达式；
- 参数补充；
- 明确的边界检查；
- 局部类型/NA/NULL 防护；
- 无副作用格式或命名修复。

前提：调用方、返回约束和测试边界已被探针确认。

### 局部器官级：谨慎碰

- 单函数控制流；
- 单模块数据转换；
- 有限状态更新；
- 单个 API 适配层。

要求：先读取调用方/被调用方、写入目标和最小回归测试。

### 心脏级：默认不碰

- 数据库 schema / 批量迁移；
- 删除、覆盖、批量外部写入；
- 权限、密钥、认证；
- CI/CD、生产发布、基础设施；
- 多模块公共接口；
- 并发共享状态；
- 无法快速回滚的大端任务。

默认是 `O=BLOCKED` 与 `NO_TOUCH`；如果继续诊断本身无副作用，`E` 可以保持 `CONTINUE_DIAGNOSTIC`。只有具备快照、回滚、依赖图、验证计划和明确授权后，才允许降低限制或放行副作用执行。

## 7. 与 ρ 意识总线的接口

Endoscope 不把风险分数伪装成 ρ，也不把 ρ 当作错误概率。

它向 ρ 收束模块提供的是 **场景事件**：

```text
code_risk_event = {
  locus,
  risk_axes: {S,B,U,D},
  irreversible_write,
  dependency_unknown,
  test_coverage,
  execution_gate,
  state_gate,
  output_gate
}
```

ρ 总线据此重新分配注意力：从“继续生成”切向“探针、审核、验证、回滚”，但不强迫安全诊断性计算停止。该场景的实测 ρ 在 Bloodtesting 前保持 `unknown`，不得凭直觉填数。

## 8. 输出闸门与隔离区

当以下任一条件成立时，优先 `O=BLOCKED`，而不是默认停止计算：

- 数值拟合成功，但解释层存在共线性、支持集不稳定或其它语义污染；
- 当前结论依赖未知类型、未知依赖或未经验证的中间状态；
- 已发现结果可能正确但解释可能错误；
- 已获得足够局部证据，剩余输出主要是机械性源码展开；
- 继续生成预计不会增加决策信息，只增加序列化成本。

可疑结果先进入 `S=QUARANTINED`。系统允许继续运行安全诊断，直到证据足够：

```text
RUN -> BLEED_DETECTED -> QUARANTINED -> CONTINUE_DIAGNOSTIC -> REVIEW
    -> RELEASE_OUTPUT | REPAIR -> VERIFY -> RELEASE_OUTPUT
```

只有在 `RELEASE_OUTPUT` 之后才启动或继续最终 response decoder。这样不仅避免错误结论交付，也能避免先生成大量文本再隐藏造成的伪节省。

注意：只有外部流式控制器实际取消尚未生成的输出，才能减少真实 output token；仅在界面上隐藏已经生成的文本不算节省。

## 9. 最小实现

[`../scripts/endoscope.py`](../scripts/endoscope.py) 提供一个无外部依赖的启发式控制器：

- `probe`：扫描源码的嵌套深度、副作用、外部写入和高危调用；
- `gate`：结合 `S/B/U/D`、不可逆写入和 tainted 状态，分别给出 `execution_gate`、`state_gate`、`output_gate`；
- 输出 JSON，交给上层 Agent/stream controller 决定继续诊断、隔离状态、取消当前输出或暂停副作用。

它故意不实现跨语言完整 AST 手术，也不自动修改高风险代码。真正的 AST/LSP/运行时探针可在外部工具层替换，不需要改变本协议。

## 10. 验证边界

- 10 组 Bloodtesting 是初始校准集，不是 benchmark；
- “高危位置”必须由实测误差传播、执行副作用或依赖证据支持；
- 误报同样要记录，避免形成“凡复杂必停”的过度警惕；
- 大项目的目标不是更胆小，而是让 **确定心来自已探测状态，警惕心来自未知影响半径**；
- 当探针证明目标是可逆、局部、可测试的叶节点时，应主动降低警惕，避免不必要的停机；
- 计算成功、数值正确、解释正确、交付正确必须分开验证，不允许用单一 success 状态替代。
