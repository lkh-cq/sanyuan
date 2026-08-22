---
name: θ次级注意力辅助
module_id: core-theta-switching
description: "θ=1-rho，只描述当前主方向之外仍需保留的注意力提示。它是 RAG 前端 advisory hint，不再拥有场景强制切换、过滤、恢复、检索或执行权限。"
version: 1.5.0
category: attention-hint
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# θ：次级注意力辅助

## 1. 定义

```text
theta = 1 - rho
rho + theta = 1
```

θ 表示**当前前端任务视图中，主方向之外仍需要保留关注的相对提示**。

它不是：

- 错误率；
- 风险概率；
- 场景切换授权；
- FilterLease 触发器；
- source revival 权限；
- RAG 召回阈值。

## 2. 唯一职责

θ 只允许进入 `RAGRequestFrame.attention_hints`，帮助下游知道哪些 secondary axes 不应被主任务完全遮蔽。

示例：

```yaml
attention_hints:
  role: advisory_only
  rho: 0.72
  theta: 0.28
  primary_axes:
    - PNPLA8
  secondary_axes:
    - mentor_disagreement
    - unresolved_question
```

这表示“不要把次级轴完全忘掉”，不表示三元必须主动检索、切换场景或恢复任何被过滤内容。

## 3. 禁止权限

```text
theta -/-> FilterLease
theta -/-> source revival
theta -/-> source deletion
theta -/-> PASS/HOLD
theta -/-> force reframe
theta -/-> retrieval execution
theta -/-> truth decision
theta -/-> generation
```

旧版本中的 `theta > threshold -> 强制切换` 属于历史运行时设计，不再是 V3.4 RAG 前端默认行为。

## 4. 与 Filter 的绝对隔离

即使 theta 很高：

- 不能恢复一个已经 SEALED 的 FilterLease；
- 不能扩大 FilterSpec；
- 不能把 HOLD 项自动重新放回 PASS；
- 不能开启一个新的 FilterLease。

如果下游 RAG 认为 secondary axes 值得扩宽检索，由下游自己决定。

## 5. 与 B_T 的关系

`B_T.attention_focus.secondary_axes` 是 θ 的主要语义来源之一。

B_T 变化时可以重新编译 attention hints，但当前 ACTIVE FilterLease 必须按棘轮规则 SEALED；是否重新授权由用户决定，而不是 theta 决定。

## 6. 历史阈值与归档

旧 θ 扫描、场景阈值和切换记录保留在 Git 历史/来源层中，不再作为前端权限规则。

任何历史数值若继续用于实验，只能标记为 experimental observation；不得把它写成用户未授权的动作门控。

## 7. 前端验收

必须验证：

1. 修改 theta 不改变 FilterLease state；
2. 修改 theta 不改变 source_refs 集合；
3. theta 不触发任何自动 PASS/HOLD/revival；
4. theta 只存在于 attention hint / audit metadata；
5. 下游 RAG 可以忽略 theta 而仍获得完整前端请求。
