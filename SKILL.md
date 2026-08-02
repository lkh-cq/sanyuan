---
name: consciousness-bus
description: "将复杂科研、写作、知识整理、项目规划或长上下文任务编译为可校验的三元三才认知预处理流程。Use when the user explicitly mentions 三元三才、意识总线、三才/三题、藏归、元信息空间/互信息空间、ρ/θ、n位聚焦、缓存波、任务边界 B_T，或要求在多个材料、约束、证据关系和子任务之间保持可追溯结构；也用于继续或修订该项目。不要因普通的一步问答而自动展开完整总线。"
---

# 三元三才·意识总线

把本 Skill 作为复杂任务的认知预处理层、临时知识图谱协议和上下文编译器。保留用户原始材料与约束，先限定任务功能边界，再组织信息及其关系；不要把该框架冒充现实机制、证明系统或通用 Agent。

项目基线为 V3.2.0。读取 [architecture.md](references/architecture.md) 取得冻结本体和权威层级。

## 先选择运行强度

| 模式 | 条件 | 最小加载 |
| --- | --- | --- |
| 直接模式 | 单一事实、一步解释、无需跨材料保持结构 | 仅保留用户约束，不显式展开总线 |
| 快筛模式 | 需要筛选、比较或压缩，但任务边界清楚 | [fast-filter-recipe.yaml](references/fast-filter-recipe.yaml) |
| 深度模式 | 多材料、多阶段、多证据关系、长期项目或用户明确调用本框架 | [research-recipe.yaml](references/research-recipe.yaml) |
| 维护模式 | 修改本体、公式、模块、配方、Schema 或版本 | 架构、清单、相关模块、Schema 与 [version-provenance.md](references/version-provenance.md) |

不要为了展示框架而把简单问题复杂化。用户明确调用某个子模块时，只加载该模块及其必需依赖。

## 执行主流程

1. **冻结输入。** 区分用户原话、源材料、既有项目定义与当前推断。以用户最新明确表述覆盖旧定义，但记录覆盖关系。
2. **编译任务边界。** 按 [task-boundary.md](references/task-boundary.md) 生成 `B_T`：任务目标、可验证功能 `F_T`、禁止损失、误差预算 `ε_T`、必需观测空间、可选观测空间、输出与停止条件。在任何过滤、归一化或藏归前完成。
3. **独立研判。** 按 [think-before-responding.md](references/think-before-responding.md) 提取主题词和自身注意向量，再与外部框架比较；不要先接受材料中的坐标系。
4. **必要时拆分。** 按 [task-decomposition.md](references/task-decomposition.md) 将复杂任务拆成可独立验证的子任务。每个子任务拥有自己的 `B_T`，合成时检查边界冲突。
5. **分离两个观测空间。**
   - 用 [sancai-store.md](references/sancai-store.md) 编码元信息空间 `M`：天才=规律，地才=环境，人才=实践。
   - 用 [hu-observation-space.md](references/hu-observation-space.md) 编码互信息空间 `H`：直接互、复合互、路径残差、流止、转换、反馈。这里的“互信息”不是信息论 mutual information。
6. **独立归一化。** 先分别运行 [meta-normalization.md](references/meta-normalization.md) 与 [hu-normalization.md](references/hu-normalization.md)，再做跨空间一致性检查。不要把 `M` 与 `H` 拼成一个向量后做一次 SVD。
7. **按需藏归。** 需要跨轮次、跨材料或文件化状态时，运行 [zang-gui-orchestrator.md](references/zang-gui-orchestrator.md)：
   - 藏只记录联系和具体内容，不替下游做价值判断。
   - 归只读取相关节点并编译上下文，不静默重写原节点。
   - 天↔地↔人中，地管理流与止但不携带固有方向。
8. **限制工作集。** 按 [n-focus.md](references/n-focus.md) 只加载当前交互命中的 `b_n`。Dijkstra 只在离线重建地址表时运行；调用时只查表，不搜索。
9. **控制收束与切换。** 用 [rho-convergence.md](references/rho-convergence.md) 管“往哪走”，用 [theta-switching.md](references/theta-switching.md) 管“何时离开当前边界”。保持 `ρ+θ=1`；不得把 ρ 称为正确率或把 θ 称为错误率。
10. **合成并校验。** 先验证每个子任务的 `F_T`、禁止损失与证据边界，再合成结论。显式标注事实、关系、推断、缺口与冲突。
11. **更新缓存相位。** 按 [cache-wave.md](references/cache-wave.md) 判断涨潮、退潮或深睡；仅在 `dθ'/dt` 加速或 `∇E` 越阈时重建。压缩前使用 [condense-protocol.md](references/condense-protocol.md) 保存注意力状态。

## 保持冻结本体

| 空间 | 三元 | 固定含义 |
| --- | --- | --- |
| 藏 | 天才 / 地才 / 人才 | 规律 / 环境 / 实践 |
| 归 | 天题 / 地题 / 人题 | 信息的本来样貌 / 读取方式 / 读取记录 |
| 拓扑 | 天 ↔ 地 ↔ 人 | 地居中，管理信息流与止，无固有方向 |
| 关系观测 | 互 | 独立关系空间；`FlowEvent ⊂ 互` |

“三元”只指天—地—人的共享三位拓扑，不另设“天元/地元/人元”作为第三套分类。不要把三才与三题合并成同一层分类。不要把地固定窄化为地理物质。不要把互新增为第四本体实体，也不要把互降格为 FlowEvent。

用户要求“用三元三才整理”时，至少显式保持：三才的三个固定标签、天↔地↔人拓扑、原始观察与关系推断的边界，以及“只记录联系、不代替下游判断”的职责。不要用新造术语替代这些标签。

## 管理运行时状态

区分两个命名空间：

- `references/` 是本 Skill 随附的只读规范，不写任务内容。
- `reference/` 是任务项目中的运行时状态根目录，仅在用户要求持久化、任务确实需要跨轮次状态、且当前工作区允许写入时创建。

运行时使用：

```text
reference/
├── source/   # 原始材料与来源指针
├── store/    # StoreNode：三才藏
├── read/     # ReadNode：三题归
├── flow/     # MutualNode / FlowEvent / CycleLink
└── routing/  # 离线生成的地址表
```

没有文件写入授权时，在当前回答内维护临时结构，不声称已落盘。写入前读取 [store-write-spec.md](references/store-write-spec.md)；读取注入前读取 [read-injection.md](references/read-injection.md)。

## 控制输出

默认先给任务结果，不强迫用户阅读内部账本。仅在结构有助于校验时附上：

1. `B_T` 摘要；
2. 元信息 `M_T` 与互信息 `H_T` 的关键保留项；
3. 被保护的路径残差、禁止损失和冲突；
4. 当前 ρ/θ 状态与停止/切换理由；
5. 证据与推断边界；
6. 下一步可验证动作。

不要伪造精确的 ρ、θ、Ω、`∇E`、`θ'` 数值。缺少可计算输入时使用定性状态或区间，并注明判定依据。

## 按需读取模块

### 核心与预处理

- 任务边界：[task-boundary.md](references/task-boundary.md)
- 元归一化：[meta-normalization.md](references/meta-normalization.md)
- 互归一化：[hu-normalization.md](references/hu-normalization.md)
- 三思而后行：[think-before-responding.md](references/think-before-responding.md)
- 子任务拆分：[task-decomposition.md](references/task-decomposition.md)
- ρ收束：[rho-convergence.md](references/rho-convergence.md)
- θ切换：[theta-switching.md](references/theta-switching.md)
- n位聚焦：[n-focus.md](references/n-focus.md)
- 缓存波与压缩：[cache-wave.md](references/cache-wave.md)、[condense-protocol.md](references/condense-protocol.md)

### 藏归与关系

- 互空间：[hu-observation-space.md](references/hu-observation-space.md)
- 藏归调度：[zang-gui-orchestrator.md](references/zang-gui-orchestrator.md)
- 三才藏：[sancai-store.md](references/sancai-store.md)、[tiancai.md](references/tiancai.md)、[dicai.md](references/dicai.md)、[rencai.md](references/rencai.md)
- 三题归：[santi-read.md](references/santi-read.md)、[tianti.md](references/tianti.md)、[diti.md](references/diti.md)、[renti.md](references/renti.md)
- 写入与读取：[store-write-spec.md](references/store-write-spec.md)、[read-injection.md](references/read-injection.md)
- 拓扑与循环：[flow-topology.md](references/flow-topology.md)、[flow-event-catalog.yaml](references/flow-event-catalog.yaml)、[zang-gui-cycle.md](references/zang-gui-cycle.md)


### 扩展与归档

- 归档方案迁移：[archive-ingestion.md](references/archive-ingestion.md)
- 三元语法阅读拓扑：[reading-topology.md](references/reading-topology.md)
- 模态可见性边界：[modality-boundary.md](references/modality-boundary.md)

### 机器约束

- 项目清单：[project-manifest.yaml](references/project-manifest.yaml)
- 状态协议：[state-protocol.schema.yaml](references/state-protocol.schema.yaml)
- Schema：[schema-task-boundary.schema.yaml](references/schema-task-boundary.schema.yaml)、[schema-meta-normalization.schema.yaml](references/schema-meta-normalization.schema.yaml)、[schema-hu-normalization.schema.yaml](references/schema-hu-normalization.schema.yaml)、[schema-mutual-node.schema.yaml](references/schema-mutual-node.schema.yaml)、[schema-attention-state.schema.yaml](references/schema-attention-state.schema.yaml)、[schema-store-node.schema.yaml](references/schema-store-node.schema.yaml)、[schema-read-node.schema.yaml](references/schema-read-node.schema.yaml)、[schema-flow-event.schema.yaml](references/schema-flow-event.schema.yaml)、[schema-cycle-link.schema.yaml](references/schema-cycle-link.schema.yaml)、[schema-recipe.schema.yaml](references/schema-recipe.schema.yaml)
- 输出契约与验收：[output-contract.md](references/output-contract.md)、[acceptance-tests.yaml](references/acceptance-tests.yaml)

修改任何本体、模块路径、配方或 Schema 后，运行 `python3 scripts/validate_bundle.py`，修复所有失败项后再交付。
