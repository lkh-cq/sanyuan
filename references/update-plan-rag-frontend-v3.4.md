# V3.4 更新计划：RAG 前端收束与过滤权限隔离

## 1. 更新目标

V3.4 不再把三元扩展成一个自带 RAG、检索、长期状态和判断权的 Agent runtime，而是收束为：

> **用户/来源材料与外部 RAG 之间的语义—拓扑前端插件。**

本轮优先修复的缺陷是：任务聚焦、B_T、多重归一化和压缩在没有用户显式授权时可以静默缩减来源信息，导致“结果看似贴题，但讨论拓扑已经被删减”的灾难性静默降级。

## 2. P0：立即阻断旧危险路径

### P0-1 默认关闭过滤权限

所有任务、所有子任务初始化：

```text
FilterLease = CLOSED
```

不得从任务复杂度、ρ/θ、B_T、n 位聚焦、缓存波、Endoscope 或 normalization 自动推导 ACTIVE。

### P0-2 Normalization 去除删除权

修改：

- `task-boundary.md`
- `meta-normalization.md`
- `hu-normalization.md`
- `schema-task-boundary.schema.yaml`
- `schema-meta-normalization.schema.yaml`
- `schema-hu-normalization.schema.yaml`

删除/废弃以下旧语义：

- `indifferent -> 可删除`；
- `任务条件压缩` 作为 normalization 的默认步骤；
- `epsilon_T` 作为默认有损压缩许可；
- `omitted_features + recovery_refs` 由默认 normalization 自动产生；
- 快速任务通过减少来源项实现“提速”。

替换为：

- lossless alignment；
- `unmapped/unresolved` 标记；
- source refs 全量保留；
- 过滤必须进入独立 FilterLease 路径。

### P0-3 ρ/θ 降级为 advisory

ρ/θ 只提供主注意力与次级注意力提示，不再承担：

- 删除/恢复来源；
- 打开/关闭过滤；
- RAG 召回策略；
- 真值判断；
- Endoscope 权限门控。

## 3. P1：重构前端合同

### P1-1 新增 `RAGRequestFrame`

前端默认输出：

- task/boundary refs；
- primary query；
- secondary axes；
- source refs；
- normalization refs；
- ρ/θ attention hints；
- optional routing metadata；
- optional FilterReceipt。

不在该合同中实现 embedding、retrieval、rerank、generation。

### P1-2 新增 FilterLease / FilterReceipt Schema

建立 machine-enforced 约束：

- `issued_by = user_explicit`；
- task-local；
- single-owner；
- non-inheritable；
- non-refreshable；
- task complete/abort/timeout/boundary/spec change 自动 SEALED；
- FilterSpec 冻结；
- PASS/HOLD 不修改来源。

### P1-3 将 fast-filter 拆成 fast-view 与 batch-filter

旧 `fast-filter-recipe.yaml` 当前同时承担“快速处理”和“过滤/压缩”两层含义，必须拆分：

1. `fast-view-recipe.yaml`：默认快速视图，lossless，不需要权限；
2. `fast-filter-recipe.yaml`：只用于用户显式授权的大批次高过滤任务，入口必须验证 ACTIVE FilterLease。

## 4. P2：现有模块职责降级

### B_T

保留：目标、功能、观测轴、注意力重点。

删除：任何隐式过滤权。

### 元/互归一化

保留：对齐、标注、坐标编译。

删除：任务相关性驱动的默认删除与压缩。

### n 位聚焦

只决定当前请求优先展开多少，不改变 source survival。

### 缓存波 / condense

只允许优化前端工作视图和引用驻留；不得据此删除来源或将摘要冒充源。

### Endoscope / NSL

降级为前端审计器：检测未授权损失、FilterLease 越权、receipt 缺失、source refs 异常消失。

不再把默认 normalization 产生的 omitted 特征当成正常运行模式。

### reader-facing-analysis

从前端核心主链移出。若保留，只作为可选展示 adapter；核心默认停在 `RAGRequestFrame`。

## 5. P3：适配器迁移

### sanyuan-context-router

保持薄客户端定位，只增加对通用前端合同的透传/展示：

- RAGRequestFrame；
- attention hints；
- filter receipt；
- source refs。

不得把插件升级成 embedding/retrieval 服务。

### visualR / java-runtime

本轮不改数学语义。

只有在前端合同稳定后，才讨论是否让它们消费 SignalEnvelope / routing metadata；仍遵守“执行实现不得自行重定义上游语义”。

### mirror-bus

继续冻结，不复活 watcher，不恢复自动跨窗口注入。

## 6. P4：自动验证与事故回放

必须新增以下验收：

1. **导师录音总结回放**：用户只要求“总结与 X 有关的重点”时，FilterLease 保持 CLOSED；来源片段和说话人/时间顺序引用不因 B_T 消失。
2. **子任务隔离**：A 有 ACTIVE lease，B/C 必须 CLOSED。
3. **任务结束棘轮**：A 完成后 lease 进入 SEALED，不能恢复。
4. **Spec 变化**：FilterSpec 改动立即 SEALED，必须重新授权。
5. **ρ/θ 隔离**：任意 ρ/θ 变化都不能改变 lease 状态。
6. **Normalization 保真**：输入 source refs 数量与输出可追溯 source refs 集合一致；无法对齐项进入 `unmapped`，不得消失。
7. **并行安全**：多个 worker 可消费同一 lease，但不能产生子 lease。
8. **前端边界**：默认路径只生成 RAGRequestFrame，不调用内建 retriever/reranker/generator。
9. **过滤可见性**：ACTIVE 任务结束必须有 FilterReceipt；无过滤时 receipt/状态必须明确 `filter_applied=false`。

## 7. 迁移顺序

```text
Phase 0  文档硬约束 + 默认 CLOSED
  -> Phase 1  Schema / validator
  -> Phase 2  task-boundary + normalization 去损失化
  -> Phase 3  fast-view / batch-filter 配方拆分
  -> Phase 4  RAGRequestFrame 主入口
  -> Phase 5  Endoscope / n-focus / cache 职责降级
  -> Phase 6  context-router 适配
  -> Phase 7  事故回放 + 前向测试
  -> Phase 8  才讨论修改 frozen architecture.md
```

## 8. 版本与发布策略

- 项目版本：只从 `project-manifest.yaml#project.version` 读取；
- `rag-frontend-governance`：0.1.0，迁移期硬约束；
- `filter-ratchet-permission`：0.1.0，实验性权限模块；
- `task-boundary`、`meta-normalization`、`hu-normalization`：迁移至 0.2.0；
- 旧 `fast-filter` 默认路由在迁移完成前视为 deprecated；
- 不在本轮自动晋升多时间尺度注意力为 frozen ontology。

## 9. Merge Gate

以下条件全部满足前，PR 保持 draft：

- active docs 中不存在“indifferent -> 可删除”的默认行为；
- active normalization schema 不要求 `omitted_features` 作为正常结果；
- task boundary 不再要求正 `epsilon_T` 作为有损预算；
- FilterLease schema 与 validator 通过；
- fast-view 与 batch-filter 权限路径分离；
- 录音总结事故回放通过；
- PR diff 中没有把 RAG/retriever/reranker/generator 实现塞进三元核心；
- `architecture.md` 是否修改由完整迁移审查决定，不因单个实验模块静默覆盖。
