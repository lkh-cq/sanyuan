---
name: multiscale-reinjection-kernel
module_id: extension-multiscale-reinjection-kernel
description: "把多时间尺度信号分层、循环语义再注入与 ρ/θ 拓扑门控组合成一个实验性最小运行核。"
version: 0.1.0
category: experimental-runtime
manifest_ref: references/project-manifest.yaml
---

# 多时间尺度语义再注入核

本模块是实验性组合层，不修改 `architecture.md` 的冻结本体。它把现有 `B_T`、元/互独立归一化、`ρ + θ = 1`、藏归、n 位聚焦、缓存波与 Endoscope 重新解释为一个事件驱动循环中的不同策略，而不是继续扩张新的平级“认知器官”。

## 1. 最小目标

运行核只冻结两个动作：

1. **语义再注入**：现实或工具产生新事件后，先按当前任务边界归一化，更新状态，再只把本轮需要的最小工作集编译为上下文。
2. **ρ/θ 门控**：`ρ + θ = 1`。ρ 表示当前方向的收束分配，θ 表示当前方向之外的分配；二者不是正确率/错误率。θ 升高时允许重构边界或恢复被压低的路径。

概念循环：

```text
observe -> normalize -> state delta -> compile/reinject
       -> rho/theta gate -> act -> observe ...
```

Transformer、检索器、R/Java 计算核、外部模型或工具都只是该循环中的算子，不是世界状态本体。

## 2. 为什么增加“信号头”，而不是只增加 embedding

不同输入不仅模态不同，还可能具有不同的更新频率、传播范围、状态寿命、来源和证据边界。因此本模块把每个可路由输入拆成：

```text
payload reference + routing header
```

`payload_ref` 指向原始内容或现有 Store/Read/Mutual/FlowEvent；路由头只描述如何处理，不复制完整内容。正式字段见 `schema-signal-envelope.schema.json`。

最小路由头包括：

- `source.kind`：来源类别，允许领域适配器自定义；
- `modality`：文本、图像、音频、表格、运行时事件等输入形态；
- `temporal.timescale`：fast / intermediate / slow / static；
- `temporal.persistence`：transient / session / persistent；
- `propagation.scope`：local / regional / global；
- `propagation.fanout`：dense / sparse / broadcast；
- `provenance` 与 `uncertainty`：证据来源和不确定性；
- `task_boundary_ref`：当前 `B_T` 引用。

这些字段是路由元数据，不是新的本体实体，也不自动等价于生物学神经、免疫、代谢或内分泌机制。生物学可以提供结构启发，但不能未经证据直接写成 AI 机制事实。

## 3. 稠密/稀疏是传播权限，不是信号身份

本模块不规定“神经=稠密、代谢=稀疏”。同一来源在不同任务里可以使用不同 fanout。默认只区分：

- `dense`：当前局部工作集内允许较高连通；
- `sparse`：只沿显式依赖、命中关系或恢复坐标传播；
- `broadcast`：写入共享慢状态，但不代表每一轮都重新 token 化。

因此稀疏/稠密是**路由策略**，不是领域标签。

## 4. 快流与慢流

运行状态分为两个时间尺度容器：

```text
S = S_fast + S_slow
```

`S_fast` 保存高频、短寿命、当前工作相关的变化；`S_slow` 保存低频、长寿命或跨轮次持续的状态。两者仍属于同一个状态空间。

关键约束：**慢状态不因每一轮推理而重复展开为完整 token。** 未变化的慢状态只保留引用；只有 `delta`、任务边界变化、跨尺度依赖命中或 θ 门控要求重构时，才进入新的再注入帧。

参考状态演化：

```text
S_fast(t+dt) = F(S_fast, delta_fast, refs(S_slow))
S_slow(t+dT) = G(S_slow, aggregate(S_fast), delta_slow)
```

其中 `dt < dT` 只是时间尺度关系，不强制具体物理时长。

## 5. 跨尺度耦合

四类路由边：

- fast -> fast：当前局部高频工作；
- slow -> slow：长期状态之间的低频更新；
- fast -> slow：高频事件积累后改变持久状态；
- slow -> fast：持久状态改变当前工作集可走的路径。

真正需要额外关注的是跨尺度边，但本模块不预设其权重。任何权重必须来自任务策略、运行观测或外部训练/校准，而不是从模块名称推导。

如果下游使用 Transformer，可把路由头转译为 attention bias / mask：

```text
logit(i,j) = q_i*k_j/sqrt(d)
           + B_source + B_time + B_scope + B_state + M_route
```

这里只定义编译接口，不宣称当前项目已经训练出这些 bias。

## 6. 与现有三元模块的组合

| 现有模块 | 在最小核中的位置 |
| --- | --- |
| `B_T` | 每轮再注入前的任务边界 |
| 元归一化 | 对对象自身属性做任务条件校准 |
| 互归一化 | 对关系、流止、路径残差做任务条件校准 |
| 藏 | 持久化具体内容和可恢复引用 |
| 归 | 按新边界重新读取/重新编译旧状态 |
| n 位聚焦 | `compile()` 的工作集预算策略 |
| 缓存波 / condense | fast/slow 状态的驻留与压缩策略 |
| Endoscope / NSL | θ 上升或新证据命中时的最小恢复策略 |
| ρ | 当前方向的收束分配 |
| θ | 边界外分配与重构门控 |

因此这些模块不需要继续互相模拟。它们都应向同一个 `observe -> normalize -> state -> reinject -> gate` 循环提供策略。

## 7. 与已有仓库的边界

- **sanyuan**：本模块的语义与协议权威来源。
- **visualR**：PAL/九宫/矩阵计算的 R 参考实现；不因本模块自动改写其数学语义。
- **java-runtime**：现有 Topology Operator ABI 与执行编排层；只有在语义契约先被验证后，才应增加信号路由实现，继续遵守“Java 不自行重定义语义”。
- **sanyuan-context-router**：薄客户端/适配器，不成为新内核；未来可只透传 SignalEnvelope 头部或调用通用 sidecar。
- **mirror-bus**：保持冻结。它只可作为历史的外部观察信号源协议参考，不得因此重启 watcher 或自动注入运行时。

## 8. Reinjection Frame

每一轮上下文编译输出一个 `ReinjectionFrame`，而不是复制整个状态：

```text
frame = {
  boundary_ref,
  delta_refs,
  persistent_refs,
  revived_refs,
  rho,
  theta,
  gate
}
```

正式合同见 `schema-reinjection-frame.schema.json`。`persistent_refs` 只是未变化慢状态的地址，不代表已把正文重新送入模型。

## 9. 门控规则

本实验模块只冻结守恒关系和行为边界：

```text
rho in [0,1]
theta = 1 - rho
```

- `CONVERGE`：当前边界继续有效，优先注入本轮 delta；
- `REFRAME`：当前边界需要重新编译，可按 `recovery_ref`/跨尺度依赖最小恢复；
- 不允许把 θ 解释为错误概率；
- 不允许仅因为来源标签为“慢信号”就强行提升或压低 ρ/θ；
- 不允许自动把实验性路由权重写回稳定策略。

阈值属于 TaskProfile/运行策略，不属于冻结本体。

## 10. 参考实现边界

`scripts/multiscale_reinjection.py` 只实现：

- SignalEnvelope 的不可变路由头；
- fast/slow 状态容器；
- delta 检测；
- 未变化 slow state 只输出引用；
- `rho + theta = 1` 门控；
- ReinjectionFrame 生成。

它**不实现** embedding、学习型 attention、概率校准、领域因果推断，也不替代现有 LLM/Transformer。

## 11. 晋升条件

本模块保持 experimental，至少完成以下证据后才可讨论进入冻结架构：

1. 在文本、代码/运行时和至少一种非文本模态上验证同一 SignalEnvelope 合同；
2. 比较“每轮重放全部慢状态”与“delta + persistent refs”的 token/延迟差异；
3. 验证 sparse/dense/broadcast 路由不会静默丢失关键依赖；
4. 验证 θ 触发最小恢复时的 Recovery Efficiency；
5. 与 visualR/java-runtime 的现有 PAL/ABI 做兼容性测试，而不是重写其语义；
6. 通过独立前向任务验证后，再决定是否修改 `architecture.md`。
