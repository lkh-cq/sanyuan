---
name: ρ主注意力辅助
module_id: core-rho-convergence
description: "ρ 只描述当前主方向的注意力收束提示，与 θ 共用 rho+theta=1。它是 RAG 前端 advisory hint，不拥有过滤、判断、检索或执行权限。"
version: 3.1.0
category: attention-hint
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# ρ：主注意力辅助

## 1. 定义

```text
rho in [0,1]
theta = 1 - rho
```

ρ 表示**当前前端任务视图中，主注意力方向的相对收束提示**。

它不表示：

- 正确率；
- 事实可信度；
- RAG 召回概率；
- 过滤强度；
- 用户授权；
- 模型质量。

## 2. 唯一职责

ρ 只允许帮助构造 `RAGRequestFrame.attention_hints`，例如：

```yaml
attention_hints:
  role: advisory_only
  rho: 0.72
  theta: 0.28
  primary_axes:
    - experiment_design
  secondary_axes:
    - unresolved_questions
```

若没有可计算依据，可以省略数值，只保留主/次注意力方向；不得伪造精确 rho。

## 3. 禁止权限

```text
rho -/-> FilterLease
rho -/-> source survival
rho -/-> PASS/HOLD
rho -/-> truth decision
rho -/-> retrieval execution
rho -/-> rerank
rho -/-> generation
rho -/-> task completion
```

ρ 高不意味着可以删除非主线信息；ρ 低也不意味着自动扩宽或恢复过滤权限。

## 4. 与 B_T 的关系

`B_T.attention_focus` 可以提供 primary/secondary axes，ρ 只对这些方向做辅助表达。

`B_T` 改变时可以重新计算 attention hints，但不能因此创建 FilterLease。

## 5. 与 θ 的关系

ρ 与 θ 是同一注意力分配轴的两个互补量：

```text
rho + theta = 1
```

二者都属于 advisory layer。

θ 可以提示“不要过度收束”，但是否扩大下游检索、如何 rerank、是否生成答案由外部 RAG 决定。

## 6. 历史向量库

旧版本中保存的注意力向量、场景经验和实验记录可作为历史来源/候选提示，不再自动成为运行时门控规则。

任何历史数值只有在来源可追溯、场景一致并经过独立验证时，才能作为当前 hint 的参考；不得把旧 rho 值当作权限或质量证明。

## 7. 前端验收

必须验证：

1. 修改 rho 不改变 FilterLease state；
2. 修改 rho 不改变 source_refs 集合；
3. rho 只能出现在 attention hint / audit metadata；
4. 无依据时不伪造数值；
5. 下游 RAG 可以完全忽略 rho 而仍能读取完整 RAGRequestFrame。
