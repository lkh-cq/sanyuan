---
name: consciousness-bus
description: "将复杂科研、写作、知识整理、项目规划或长上下文任务编译为可校验的三元三才 RAG 前端请求。Use when the user explicitly mentions 三元三才、意识总线、三才/三题、藏归、元信息空间/互信息空间、ρ/θ、n位聚焦、缓存波、任务边界 B_T、Endoscope、Bloodtesting、代码内窥镜，或要求在多个材料、约束、证据关系和子任务之间保持可追溯结构；也用于继续或修订该项目。不要因普通的一步问答而自动展开完整总线。"
---

# 三元三才·RAG 前端插件

把本 Skill 作为**用户/来源材料与外部 RAG 之间的语义—拓扑前端**。它负责保真解析、任务边界、元/互对齐、注意力提示和请求编译；它不是 RAG 本身，不实现 embedding、retrieval、rerank、generation 或长期真值数据库。

项目版本只从 [project-manifest.yaml](references/project-manifest.yaml) 的 `project.version` 读取。三才、三题、互等冻结本体仍以 [architecture.md](references/architecture.md) 为权威；V3.4 迁移期间，信息损失、过滤权限和 RAG 边界必须同时遵守 [rag-frontend-governance.md](references/rag-frontend-governance.md)。

## P0 权限硬约束

1. **默认不允许过滤。** 每个任务/子任务初始化 `FilterLease=CLOSED`。
2. **Focus is priority, not filter.** `B_T`、n 位聚焦、ρ/θ 只影响当前展开/注意力，不赋予来源删减权。
3. **Normalization is lossless alignment.** 元/互归一化只能对齐和标记；无法对齐项进入 `unmapped/unresolved`，不得默认进入 omitted/delete。
4. **过滤必须手动授权。** 只有用户对当前子任务显式授权，且属于大批次+高过滤+冻结 FilterSpec，才可激活 [filter-ratchet-permission.md](references/filter-ratchet-permission.md)。
5. **权限是棘轮。** task-local、single-owner、one-shot、不可继承、不可刷新；任务完成/终止/超时/B_T变化/spec变化后立即 SEALED。
6. **Filter 不判断。** Filter 只执行被冻结的字段/标签/阈值规则，输出 PASS/HOLD；不生成“重要/相关/有价值”等语义判断。
7. **rho/theta are advisory only.** `ρ + θ = 1` 只写入主/次注意力提示；不能改 FilterLease、source survival、真值或检索执行。
8. **No silent degradation.** 发生 ACTIVE 过滤必须生成 FilterReceipt；没有过滤时明确 `filter_applied=false`。

## 运行模式

| 模式 | 条件 | 最小加载 |
| --- | --- | --- |
| 直接模式 | 单一事实/一步查询编译 | 仅保留用户约束与 source refs |
| 快速视图 | 简单任务、低成本前端编译 | [fast-view-recipe.yaml](references/fast-view-recipe.yaml) |
| 深度前端 | 多材料、多阶段、多证据关系 | [research-recipe.yaml](references/research-recipe.yaml) |
| 大批次高过滤 | 用户对当前子任务显式授权 + large batch + high filter | [fast-filter-recipe.yaml](references/fast-filter-recipe.yaml) + [filter-ratchet-permission.md](references/filter-ratchet-permission.md) |
| 代码审计 | 用户明确调用 Endoscope/Bloodtesting 或代码前端审计 | [endoscopic-code-actuation.md](references/endoscopic-code-actuation.md)，但不得绕过前端权限规范 |
| 维护模式 | 修改本体、协议、Schema、版本 | 架构、清单、规范、迁移记录与 validators |

**快速视图不等于快速过滤。** 未出现明确 FilterLease 时，不得自动进入 batch-filter。

## 前端主流程

1. **冻结来源。** 区分用户原话、来源材料、既有定义与当前推断；所有 source refs 先建立可追溯入口。
2. **编译子任务边界。** 按 [task-boundary.md](references/task-boundary.md) 生成 `B_T`。每个子任务的 FilterLease 重新初始化为 CLOSED。
3. **必要时拆分。** 子任务结果可传递，过滤权限不可传递。
4. **元/互保真对齐。** 分别运行 [meta-normalization.md](references/meta-normalization.md) 与 [hu-normalization.md](references/hu-normalization.md)。不得因为任务相关性减少 source/relation refs。
5. **一致性诊断。** 元/互不一致时标记 unresolved/diagnostic，不自动删除任何一侧。
6. **按需组织引用。** 藏归只组织来源、内容与关系引用；不得把摘要替代源。
7. **限制展开预算。** n 位聚焦可以少展开，但未展开项仍保留 source/ref。
8. **生成注意力提示。** ρ/θ 只提供 advisory attention hints。
9. **可选过滤。** 只有 ACTIVE FilterLease 才执行 frozen FilterSpec；Filter 只 PASS/HOLD，不修改来源。
10. **编译请求。** 默认输出 [schema-rag-request-frame.schema.json](references/schema-rag-request-frame.schema.json) 对应的 `RAGRequestFrame`；到此停止。
11. **交给外部 RAG。** embedding、召回、rerank、答案生成由下游系统负责。

## Endoscope / NSL 迁移边界

Endoscope 不再把默认 normalization 的信息省略视为正常路径。V3.4 前端中，它只能审计：

- normalization 是否发生未授权 source/ref 损失；
- FilterLease 是否越权、继承、续期或跨任务传播；
- FilterReceipt 是否存在；
- 过滤后的 HOLD 是否仍可从 source state 恢复。

旧 `omitted_features + recovery_refs` 只允许出现在历史兼容或明确授权的 filter view；不得由默认 normalization 新生成。

## 多时间尺度路由实验

当任务研究来源区分、快/慢信号、dense/sparse/broadcast 路由时，可读取 [multiscale-reinjection-kernel.md](references/multiscale-reinjection-kernel.md)。该模块仅定义 RAG 前端 routing metadata；不拥有 Transformer、持久世界状态或过滤权限。

## 输出合同

前端默认交付：

```text
RAGRequestFrame
- task_id / boundary_ref
- primary_query / secondary_axes
- source_refs
- normalization_refs
- attention_hints (rho/theta, advisory_only)
- routing_metadata_refs (optional)
- filter { filter_applied, lease_ref, receipt_ref }
```

三元默认不把自身生成的自然语言答案冒充 RAG 结果。`reader-facing-analysis` 在 V3.4 迁移期降为可选展示 adapter，不属于前端核心终点。

## 按需读取

### 权限与前端边界

- [rag-frontend-governance.md](references/rag-frontend-governance.md)
- [filter-ratchet-permission.md](references/filter-ratchet-permission.md)
- [update-plan-rag-frontend-v3.4.md](references/update-plan-rag-frontend-v3.4.md)
- [task-boundary.md](references/task-boundary.md)
- [fast-view-recipe.yaml](references/fast-view-recipe.yaml)
- [fast-filter-recipe.yaml](references/fast-filter-recipe.yaml)

### 元/互与藏归

- [meta-normalization.md](references/meta-normalization.md)
- [hu-normalization.md](references/hu-normalization.md)
- [sancai-store.md](references/sancai-store.md)
- [hu-observation-space.md](references/hu-observation-space.md)
- [zang-gui-orchestrator.md](references/zang-gui-orchestrator.md)

### 注意力与实验模块

- [rho-convergence.md](references/rho-convergence.md)
- [theta-switching.md](references/theta-switching.md)
- [n-focus.md](references/n-focus.md)
- [multiscale-reinjection-kernel.md](references/multiscale-reinjection-kernel.md)
- [endoscopic-code-actuation.md](references/endoscopic-code-actuation.md)

### Schema 与校验

- [project-manifest.yaml](references/project-manifest.yaml)
- [schema-task-boundary.schema.yaml](references/schema-task-boundary.schema.yaml)
- [schema-meta-normalization.schema.yaml](references/schema-meta-normalization.schema.yaml)
- [schema-hu-normalization.schema.yaml](references/schema-hu-normalization.schema.yaml)
- [schema-filter-lease.schema.json](references/schema-filter-lease.schema.json)
- [schema-rag-request-frame.schema.json](references/schema-rag-request-frame.schema.json)

修改本体、协议、Schema 或配方后必须运行仓库 validators，并执行独立前向测试。确定性校验只能证明合同一致，不能冒充语义正确性或外部 RAG 质量证明。
