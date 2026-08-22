---
name: rag-frontend-governance
module_id: governance-rag-frontend-boundary
description: "三元作为 RAG 前端插件的职责、权限与信息保真规范；冻结候选约束，禁止把注意力、归一化或任务边界升级为自动过滤权。"
version: 0.1.0
category: governance
manifest_ref: references/project-manifest.yaml
---

# RAG 前端职责与权限规范

## 0. 规范状态

本文件是 V3.4 迁移期的**前端权限硬约束**。它不重写三才、三题、互等冻结本体；它只约束三元在 RAG 前端位置上的职责、信息损失权限和输出合同。

在 V3.4 迁移完成前，若旧模块文档把 `B_T`、归一化、ρ/θ、n 位聚焦、缓存波或 Endoscope 描述成可自行删除信息，本文件优先用于判定该行为为**禁止的旧行为**，并进入迁移清单。

## 1. 项目定位

三元是 **RAG 前端预处理插件（RAG front-end preprocessor）**，不是 RAG 本身，也不是通用 Agent runtime。

三元允许负责：

- 接收用户任务与来源材料引用；
- 编译任务边界 `B_T`；
- 做保真语义/术语/单位/来源/关系对齐；
- 生成主注意力辅助信息；
- 在用户显式授权时执行一次性的批量机械过滤；
- 把结果编译为下游 RAG 可消费的查询与路由提示。

三元不得自行负责：

- embedding 生成与向量库实现；
- 召回、rerank、数据库查询策略；
- 长期知识库真值维护；
- 下游答案生成或事实裁决；
- 模型训练、梯度更新或 learned attention；
- 未经用户授权的信息删减。

形式化边界：

```text
Source/User
   -> Sanyuan Front-end
      -> RAGRequestFrame / routing hints
         -> External RAG / retriever / reranker / generator
```

## 2. 核心权责分离

### 2.1 任务边界 `B_T`

`B_T` 只描述“当前子任务在做什么、应重点关注什么、需要哪些观测轴”。

`B_T` **不是过滤许可证**，不得单独授权删除、隐藏、压缩或阻断任何来源信息。

约束：

```text
B_T -> attention/view scope
B_T -/-> filter permission
```

### 2.2 ρ / θ

`ρ + θ = 1` 只作为主注意力辅助：

- ρ：当前方向的收束提示；
- θ：当前方向之外仍需保留关注的提示。

二者不是正确率/错误率，也不是检索器、过滤器或权限控制器。

强约束：

```text
rho/theta -> attention hints only
rho/theta -/-> FilterLease
rho/theta -/-> source deletion
rho/theta -/-> truth decision
rho/theta -/-> retrieval execution
```

### 2.3 Normalization

归一化只允许**改变表示，不改变信息生存权**。

允许：

- 术语、别名、单位、编码、时间尺度、来源、模态与关系坐标对齐；
- 建立可比较的元/互视图；
- 给无法对齐的内容打 `unmapped` / `unresolved` 标记。

禁止：

- 根据任务相关性删除来源项；
- 把 `indifferent` 解释为“可删除”；
- 用 `epsilon_T`、ρ/θ、SVD 或其它启发式自动授权有损压缩；
- 通过只保留 `recovery_ref` 来掩盖实际发生的默认信息损失。

默认归一化必须满足：

```text
source item survival is preserved
source relation survival is preserved
representation may change; source refs may not disappear
```

### 2.4 Filter

Filter 是独立权限域。它不是 Normalizer，也不是 Judge。

Filter 只有在 `FilterLease` 已由用户针对**当前子任务**手动授权，并且任务同时处于大批次处理与高过滤模式时才能激活。

Filter 只执行被冻结的机械条件：

```text
PASS | HOLD
```

Filter 不生成过滤条件，不解释“重要/不重要”，不做因果、价值、真实性或科研意义判断。

如果条件需要语义判断，必须先由独立的标注/判断阶段产生显式字段或标签；Filter 只能对该字段执行用户已授权的规则。

## 3. 单任务棘轮权限

过滤权限采用 task-local、single-owner、one-shot 的棘轮模型。正式协议见 `filter-ratchet-permission.md`。

核心规则：

```text
CLOSED
  -- user explicit authorization --> ARMED(task_id)
  -- large-batch + high-filter + frozen spec --> ACTIVE(task_id)
  -- complete/abort/timeout/boundary-change/spec-change --> SEALED
```

`SEALED` 为终态；再次过滤必须创建新 lease。

权限不可继承：

```text
result may propagate
permission may not propagate
```

父任务、子任务、兄弟任务均不得继承另一个任务的 FilterLease。

并行 worker 可以消费同一个 lease，但不能复制、扩大、续期或再授权该 lease。

## 4. 来源保真与视图关系

来源材料始终位于视图之外的权威输入层：

```text
Source State >= Front-end View >= Filtered Candidate View
```

过滤只能改变“哪些引用进入本次下游请求”，不能修改或销毁来源材料本身。

特别约束：

- “总结”“聚焦”“只重点讲 X”默认只改变输出/注意力优先级，不等于授权过滤来源；
- 录音、访谈、会议、实验日志、原始数据、代码、合同等证据型来源，在没有 FilterLease 时不得因为任务主题而缩减来源拓扑；
- `OUT_OF_FOCUS`、`DORMANT`、`UNMAPPED` 都不等于 `FILTERED`。

## 5. 禁止静默降级

任何 ACTIVE FilterLease 都必须产生最小可见的 `FilterReceipt`：

- `task_id`；
- `lease_id`；
- 用户授权来源；
- 冻结 filter spec；
- PASS 数量；
- HOLD 数量；
- source mutation = false；
- lease final state = SEALED。

用户无需查看内部账本，但系统不得让“发生过高过滤”在交付层完全不可见。

没有 FilterLease 时，receipt 必须明确为：

```text
filter_applied: false
```

## 6. RAG 前端输出合同

三元默认输出的是**请求帧**，而不是下游答案：

```text
RAGRequestFrame
- task_id
- boundary_ref
- primary_query
- secondary_axes
- source_refs
- normalization_refs
- attention_hints (rho/theta; advisory only)
- routing_metadata_refs (optional)
- filter_receipt_ref (optional)
```

下游 RAG 是否检索、如何召回、如何 rerank、是否生成答案，不属于本插件的权限范围。

## 7. 多时间尺度信号的正确位置

SignalEnvelope / fast-slow / dense-sparse-broadcast 仅作为**前端路由元数据**与下游接口实验，不代表三元拥有自己的 Transformer、向量库或持久状态引擎。

可以描述：

- 来源；
- 模态；
- 时间尺度；
- 持续性；
- 传播范围；
- 路由建议。

不得据此自动删除来源，也不得把生物学类比固化成 AI 机制事实。

## 8. Endoscope / NSL 的边界

Endoscope 在前端只能审计：

- normalization 是否发生未授权损失；
- FilterLease 是否越权；
- FilterReceipt 是否完整；
- source ref 是否在无授权情况下消失。

旧设计中的 `omitted_features + recovery_refs` 不再能由默认 normalization 自动产生。只有明确的、已授权的 filter view 才允许出现 HOLD/omitted 状态；且来源仍保持可恢复、不可变。

## 9. Fail-closed 规则

以下任一条件不明确时，一律视为 `FilterLease = CLOSED`：

- 用户是否真的要求过滤；
- 当前过滤是否属于这个子任务；
- 是否属于大批次处理；
- 用户是否要求高过滤；
- filter spec 是否冻结；
- spec 是否依赖模糊语义判断；
- 任务边界是否已经变化。

无法确认时，只允许继续做保真归一化、排序、标记和查询编译。

## 10. 验收不变量

V3.4 至少必须自动验证：

1. 无授权时 normalization 不减少 source refs；
2. `B_T` 不能生成或激活 FilterLease；
3. ρ/θ 不能修改 FilterLease 状态；
4. 每个子任务默认 `CLOSED`；
5. 一个任务的 lease 不可传给任何其它任务；
6. task complete/abort/timeout/boundary-change/spec-change 后 lease 必须 SEALED；
7. SEALED lease 不可恢复；
8. Filter 只执行 frozen spec；
9. 并行 worker 不可生成子 lease；
10. 录音/会议总结在无授权时不得按主题删除讨论片段；
11. 前端默认交付 `RAGRequestFrame`，不把自身声明成 retriever/reranker/generator。
