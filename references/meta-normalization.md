---
name: meta-normalization
module_id: preprocessor-meta-normalization
description: "元信息空间独立归一化。只负责保真对齐与标注，不拥有过滤、压缩或删除权限。输出可追溯的 M_T 元信息视图。"
category: preprocessor
version: 0.2.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# 元信息空间归一化

> 输入：`B_T + raw_material`
>
> 输出：`M_T` 元信息对齐视图。
>
> **Normalization changes representation, not information survival.**

## 1. 权限边界

元归一化只允许：

- 实体/术语/别名对齐；
- 单位、编码、来源、时间尺度等表示对齐；
- 三才轴上的属性提取与标注；
- 无法对齐时标记 `unmapped` / `unresolved`；
- 为下游 RAG 请求生成可追溯引用。

元归一化禁止：

- 根据任务相关性删除特征；
- 把 `indifferent` 解释为“可删除”；
- 用 `epsilon_T`、ρ/θ、SVD、n 位聚焦或 Endoscope 自动压缩来源；
- 只留下 `recovery_ref` 而让原特征从正常视图不可见；
- 创建或激活 FilterLease。

若需要高过滤，必须走独立 `filter-ratchet-permission.md` 路径。

## 2. 元信息空间

三才仍作为默认元信息编码轴：

```text
天才 = 规律
地才 = 环境
人才 = 实践
```

元信息空间可以包含来源、置信度、模态、时间尺度等补充属性，但本模块不据此判断信息“重要/不重要”。

## 3. 输入

```yaml
input:
  B_T:
    task_id: ...
    boundary_id: ...
    meta_axes: [...]
    attention_focus: {...}
    preservation_requirements: [...]
  raw_material:
    - id: source_item_001
      content_ref: ...
      source_node_refs: [...]
```

`B_T` 只决定本轮优先展开哪些轴，不授予删除权限。

## 4. 输出

```yaml
meta_view:
  representation_id: mt_...
  boundary_id: bt_...
  observation_system: meta
  axes:
    - tiancai
    - dicai
    - rencai
  route_code: "101"
  continuous_signal:
    tiancai: 0.8
    dicai: 0.4
    rencai: 0.9
  source_item_refs:
    - source_item_001
  source_node_refs:
    - store_...
  aligned_features:
    - feature_ref: f_001
      source_ref: source_item_001
      normalized_label: ...
  unmapped_features:
    - feature_ref: f_019
      source_ref: source_item_001
      reason: unresolved_alias
  coverage:
    source_items_in: 12
    source_items_traceable_out: 12
  valid: true
```

### 关键不变量

```text
set(source_items_in) subset_of traceable_source_refs(M_T)
```

不能因为某一轴没有展开，就让对应来源项失去可追溯性。

## 5. 流程

### 步骤 1：加载 B_T 轴与 attention focus

只决定本轮**优先对齐/展开**的属性，不决定来源 survival。

### 步骤 2：元特征提取

按需要提取：

- 天才：规律、周期、阈值、约束；
- 地才：环境、载体、边界、保存条件；
- 人才：实践、实验、观察、记录方式。

每个特征必须保留 `source_ref`。

### 步骤 3：表示对齐

允许：

- 别名统一；
- 单位换算后的统一表示；
- 编码标准化；
- 来源字段补齐；
- 同义实体归并时保留原始别名列表。

不得把“与当前 task_goal 低相关”作为删除条件。

### 步骤 4：未解析项保留

无法对齐的特征进入：

```text
unmapped_features / unresolved_features
```

而不是 omitted。

### 步骤 5：路由信号编码

`s_M` 与 `q_M` 只能用于前端路由/查询提示，不用于质量、真实性或过滤判断。

### 步骤 6：保真检查

至少验证：

- 每个 source item 仍有可追溯引用；
- preservation requirements 均可定位；
- unmapped 项没有静默消失；
- 本模块没有写 FilterLease。

## 6. 与 Filter 的边界

若当前任务存在 ACTIVE FilterLease：

1. Filter 先对**来源引用集合**执行已冻结 PASS/HOLD 规则；
2. 元归一化只处理 Filter 传入的 candidate view；
3. HOLD 项仍保留在 source state 和 FilterReceipt 中；
4. 元归一化不得扩大或缩小 FilterSpec。

如果 FilterLease 不是 ACTIVE，则所有来源引用进入对齐视图。

## 7. SVD

SVD 仅可作为结构诊断工具，不作为过滤、压缩或来源生存门控。

## 8. 独立性约束

本模块：

- 不依赖互归一化；
- 不依赖 ρ/θ；
- 不依赖缓存波；
- 不调用 RAG retriever/reranker/generator；
- 不生成最终答案；
- 不修改原始来源。

默认输出用于 `RAGRequestFrame` 编译。
