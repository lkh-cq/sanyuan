---
name: consciousness-bus
description: "将复杂科研、写作、知识整理、项目规划或长上下文任务编译为可校验的三元三才认知预处理流程。Use when the user explicitly mentions 三元三才、意识总线、三才/三题、藏归、元信息空间/互信息空间、ρ/θ、n位聚焦、缓存波、任务边界 B_T、Endoscope、Bloodtesting、代码内窥镜，或要求在多个材料、约束、证据关系和子任务之间保持可追溯结构；也用于继续或修订该项目。不要因普通的一步问答而自动展开完整总线。"
---

# 三元三才·意识总线

把本 Skill 作为复杂任务的认知预处理层、临时知识图谱协议和上下文编译器。保留用户原始材料与约束，先限定任务功能边界，再组织信息及其关系；不要把该框架冒充现实机制、证明系统或通用 Agent。

项目版本只从 [project-manifest.yaml](references/project-manifest.yaml) 的 `project.version` 读取。冻结本体与职责边界只以 [architecture.md](references/architecture.md) 为权威；不要在本入口另建副本。

## 先选择运行强度

| 模式 | 条件 | 最小加载 |
| --- | --- | --- |
| 直接模式 | 单一事实、一步解释、无需跨材料保持结构 | 仅保留用户约束，不显式展开总线 |
| 快筛模式 | 需要筛选、比较或压缩，但任务边界清楚 | [fast-filter-recipe.yaml](references/fast-filter-recipe.yaml) |
| 深度模式 | 多材料、多阶段、多证据关系、长期项目或用户明确调用本框架 | [research-recipe.yaml](references/research-recipe.yaml) |
| 代码干预模式 | 代码生成/修改存在深层嵌套、未知依赖、外部写入或用户明确调用 Endoscope/Bloodtesting | [endoscopic-code-actuation.md](references/endoscopic-code-actuation.md) |
| 维护模式 | 修改本体、公式、模块、配方、Schema 或版本 | 架构、清单、来源、相关模块与 [version-provenance.md](references/version-provenance.md) |

不要为了展示框架而把简单问题复杂化。用户明确调用某个子模块时，只加载该模块及其必需依赖。

代码干预模式不是独立 Agent：先编译任务边界，再让 Endoscope 使用最小探针确认风险位置；当继续生成只会扩大未知假设或机械展开源码时，允许 `CUT_OUTPUT` 转入审核。心脏级路径默认 `NO_TOUCH`，不得因为模型“看起来有把握”就自动降低权限。

## 执行主流程

1. **冻结输入。** 区分用户原话、源材料、既有项目定义与当前推断。以用户最新明确表述覆盖旧定义，但记录覆盖关系。
2. **编译任务边界。** 按 [task-boundary.md](references/task-boundary.md) 生成 `B_T`，并在任何过滤、归一化或藏归前完成。
3. **独立研判。** 按 [think-before-responding.md](references/think-before-responding.md) 提取主题词和自身注意向量，再与外部框架比较。
4. **必要时拆分。** 按 [task-decomposition.md](references/task-decomposition.md) 给每个子任务建立独立边界，合成时检查冲突。
5. **分离观测空间。** 用 [sancai-store.md](references/sancai-store.md) 编码元信息 `M`，用 [hu-observation-space.md](references/hu-observation-space.md) 编码关系 `H`。
6. **独立归一化。** 分别运行 [meta-normalization.md](references/meta-normalization.md) 与 [hu-normalization.md](references/hu-normalization.md)，再做跨空间一致性检查。
7. **按需藏归。** 需要跨材料或文件化状态时，运行 [zang-gui-orchestrator.md](references/zang-gui-orchestrator.md)。写入前读取 [store-write-spec.md](references/store-write-spec.md)，把可检索事务登记为耦合态；不要把内容节点与关系节点压成同一字段。
8. **限制工作集。** 按 [n-focus.md](references/n-focus.md) 只加载当前交互命中的 `b_n`。离线重建地址表，调用时只查表。
9. **控制收束与切换。** 用 [rho-convergence.md](references/rho-convergence.md) 管收束方向，用 [theta-switching.md](references/theta-switching.md) 管边界切换。
10. **代码风险干预（按需）。** 涉及代码生成/修改且存在嵌套、未知依赖、外部写入或高影响半径时，读取 [endoscopic-code-actuation.md](references/endoscopic-code-actuation.md)。先 `PROBE`，再依据 `S/B/U/D` 和实际副作用决定继续、`CUT_OUTPUT -> REVIEW` 或 `NO_TOUCH`；不要把启发式风险分数伪装成错误概率或 ρ。
11. **合成、转译并校验。** 先在内部检查禁止损失、证据边界和冲突，再按 [reader-facing-analysis.md](references/reader-facing-analysis.md) 转译为自然语言结果。
12. **更新缓存相位。** 按 [cache-wave.md](references/cache-wave.md) 判断涨潮、退潮或深睡；压缩前使用 [condense-protocol.md](references/condense-protocol.md) 保存注意力状态。

执行中始终服从 [architecture.md](references/architecture.md) 的冻结定义与 [framework-pitfalls.md](references/framework-pitfalls.md) 的反例免疫规则。旧材料若与当前本体冲突，只作为来源或迁移候选，不静默复活。

## 管理运行时状态

区分两个命名空间：

- `references/` 是本 Skill 随附的只读规范，不写任务内容。
- `reference/` 是任务项目中的运行时状态根目录，仅在用户要求持久化、任务确实需要跨轮次状态且当前工作区允许写入时创建。

运行时使用 `reference/source/`、`reference/store/`、`reference/read/`、`reference/flow/` 与 `reference/routing/`。没有写入授权时，在当前回答内维护临时结构，不声称已落盘。读取注入前加载 [read-injection.md](references/read-injection.md)。

## 控制输出

默认先给任务结果，并把内部节点、边、路径和证据判断编译为简明、连贯、可独立阅读的自然语言。文献分析正文优先使用连续的段落级分析句，展开“作者写了什么—如何承接或推进—证据支持到哪里”。

代码干预模式下，完整源码不是默认交付协议。若模型已经给出足够的修改意图、目标节点和约束，且剩余生成主要是机械序列化，可由外部流式控制器执行 `CUT_OUTPUT`，转交 AST/LSP/运行时工具完成局部动作与验证。只有真正取消尚未生成的输出才计为 output 成本节省；隐藏已经生成的文本不算。

不要在默认交付中直接展示内部变量、节点编号、关系代码、裸箭头、YAML 账本或未注释简图。图表只有在显著提升理解时才作为补充，并写全名称、关系含义、证据来源和必要图例。

只有用户明确要求查看框架、内部过程、机器表示或审计记录时，才在主要结果之后附独立审计块。缺少可计算输入时使用定性状态或区间，不伪造精确数值。

## 按需读取模块

### 来源与边界

- 冻结架构：[architecture.md](references/architecture.md)
- 原始用户锚点：[original-anchors.md](references/original-anchors.md)
- 三元道辩浓缩来源：[sanyuan-daobian-framework.md](references/sanyuan-daobian-framework.md)
- 版本与迁移：[version-provenance.md](references/version-provenance.md)、[archive-ingestion.md](references/archive-ingestion.md)
- 反例免疫：[framework-pitfalls.md](references/framework-pitfalls.md)

### 核心、藏归与关系

- 任务与控制：[task-boundary.md](references/task-boundary.md)、[task-decomposition.md](references/task-decomposition.md)、[rho-convergence.md](references/rho-convergence.md)、[theta-switching.md](references/theta-switching.md)、[n-focus.md](references/n-focus.md)
- 藏归：[sancai-store.md](references/sancai-store.md)、[santi-read.md](references/santi-read.md)、[zang-gui-orchestrator.md](references/zang-gui-orchestrator.md)
- 关系与流止：[hu-observation-space.md](references/hu-observation-space.md)、[flow-topology.md](references/flow-topology.md)、[zang-gui-cycle.md](references/zang-gui-cycle.md)
- 实验性矩阵：[yijing-coupling-matrix.md](references/yijing-coupling-matrix.md)

### 代码风险干预

- Endoscope/Bloodtesting 协议：[endoscopic-code-actuation.md](references/endoscopic-code-actuation.md)
- 10 组校准夹具：[endoscope-bloodtesting.yaml](references/endoscope-bloodtesting.yaml)
- 最小控制器：`scripts/endoscope.py`

### 阅读、交付与模态

- 三元语法阅读拓扑：[reading-topology.md](references/reading-topology.md)
- 读者端分析交付：[reader-facing-analysis.md](references/reader-facing-analysis.md)
- 模态可见性边界：[modality-boundary.md](references/modality-boundary.md)
- 输出契约与验收：[output-contract.md](references/output-contract.md)、[acceptance-tests.yaml](references/acceptance-tests.yaml)

### 机器约束

- 项目清单：[project-manifest.yaml](references/project-manifest.yaml)
- 状态协议：[state-protocol.schema.yaml](references/state-protocol.schema.yaml)
- Schema：按清单 `schemas` 节读取；耦合态使用 [schema-coupling-state.schema.yaml](references/schema-coupling-state.schema.yaml)

修改任何本体、模块路径、配方或 Schema 后，运行 `python3 scripts/validate_bundle.py`，并用独立任务前向测试语义行为；确定性脚本不冒充语义证明。
