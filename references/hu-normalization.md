---
name: hu-normalization
module_id: preprocessor-hu-normalization
description: "互信息空间独立归一化。只负责关系保真对齐与标注，不拥有过滤、压缩或删除权限。输出可追溯的 H_T 关系视图。"
category: preprocessor
version: 0.2.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# 互信息空间归一化

> 输入：`B_T + raw_relations`
>
> 输出：`H_T` 关系对齐视图。
>
> **Normalization changes representation, not relation survival.**

## 1. 权限边界

互归一化只允许：

- 对直接互、复合互、路径残差、流止、转换、反馈、条件与时序关系做结构化对齐；
- 统一 relation type、条件字段、端点引用与时间/来源表示；
- 无法解析时标记 `unmapped_relations` / `unresolved_relations`；
- 为下游 RAG 请求生成关系路由提示。

互归一化禁止：

- 根据任务相关性删除关系；
- 把 `indifferent` 解释为“可删除”；
- 用 `epsilon_T`、ρ/θ、n 位聚焦、SVD 或 Endoscope 自动压缩关系；
- 因为只展开 direct 轴就让 composite/path residual 来源关系失去可追溯性；
- 创建或激活 FilterLease。

若需要大批次高过滤，必须进入独立 FilterLease 路径。

## 2. 互信息空间

互仍是独立关系观测空间，FlowEvent 只是其子类型。

可包含：

```text
直接互
复合互
路径残差
流止互
转换互
反馈互
条件互
时序互
```

关系视图不负责判断关系真假；证据状态与来源应保留给下游验证。

## 3. 输入

```yaml
input:
  B_T:
    task_id: ...
    boundary_id: ...
    hu_axes: [...]
    attention_focus: {...}
    preservation_requirements: [...]
  raw_relations:
    - relation_id: rel_001
      source_ref: source_item_001
      source: A
      target: B
      relation_type: direct
      conditions: [...]
```

`B_T` 只控制本轮优先展开的关系轴，不授予删除权限。

## 4. 输出

```yaml
mutual_view:
  representation_id: ht_...
  boundary_id: bt_...
  observation_system: hu
  axes:
    - direct
    - composite
    - path_residual
  route_code: q_H
  continuous_signal: {...}
  relation_refs:
    - rel_001
  aligned_relations:
    - relation_ref: rel_001
      endpoint_refs: [A, B]
      relation_type: direct
      conditions: [...]
      source_ref: source_item_001
  unresolved_relations:
    - relation_ref: rel_019
      source_ref: source_item_009
      reason: unresolved_endpoint
  path_residual_refs:
    - pr_001
  coverage:
    relations_in: 27
    relations_traceable_out: 27
  valid: true
```

### 关键不变量

```text
set(raw_relation_refs) subset_of traceable_relation_refs(H_T)
```

关系是否被“重点展开”与关系是否“仍然存在”必须分离。

## 5. 流程

### 步骤 1：加载 B_T 轴与 attention focus

决定本轮优先展开哪些关系，但不改变 relation survival。

### 步骤 2：关系提取与类型对齐

统一 direct/composite/path_residual/flow/transform/feedback 等表示；每条关系保留 source_ref 与 endpoint_refs。

### 步骤 3：条件与路径对齐

复合路径、路径残差、成立条件和时间关系都保留可追溯引用。

快速视图可以不展开完整正文，但必须保留 reference 和 unresolved 标记。

### 步骤 4：未解析项保留

无法解析的关系进入：

```text
unmapped_relations / unresolved_relations
```

而不是 omitted。

### 步骤 5：路由信号编码

`s_H` 与 `q_H` 只能用于查询/路由提示，不用于质量判断、真实性判断或过滤权限。

### 步骤 6：保真检查

至少验证：

- raw relation refs 仍可追溯；
- path residual refs 未静默消失；
- preservation requirements 指定的关系仍可定位；
- unresolved 项没有被吞掉；
- 本模块没有写 FilterLease。

## 6. 跨空间一致性

元/互都改为无损对齐后，跨空间检查不再用于“决定该恢复哪些被删内容”。

它只检查：

```text
M_T 中的对象引用是否能解释 H_T 端点
H_T 中的关系引用是否都有来源与端点
unresolved 是否需要下游 RAG/人工继续处理
```

如果发现不一致：

```text
mark unresolved / emit diagnostic
```

而不是自动删除另一侧信息。

## 7. 与 Filter 的边界

若存在 ACTIVE FilterLease：

1. Filter 先对来源/关系引用执行 frozen spec；
2. H_T 只对 PASS candidate view 做结构化展开；
3. HOLD relations 仍存在于 source state 和 FilterReceipt；
4. H_T 不得重新判断 HOLD/PASS，也不得扩大 spec。

没有 ACTIVE FilterLease 时，所有关系引用都必须保持可追溯。

## 8. 独立性约束

本模块：

- 不依赖元归一化；
- 不依赖 ρ/θ；
- 不依赖缓存波；
- 不调用 RAG retriever/reranker/generator；
- 不生成最终答案；
- 不修改来源关系。

默认输出用于 `RAGRequestFrame` 编译。
