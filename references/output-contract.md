# 输出契约

## 目录

1. 默认回答
2. 可审计回答
3. 文件化状态
4. 证据边界
5. 停止条件

## 默认回答

先回答用户实际问题。不要把三元三才术语当作装饰性前言，也不要在简单任务中展示完整总线。

复杂任务可在结果后附一个最小审计块：

```yaml
boundary:
  goal: ""
  forbidden_loss: []
  stop_condition: ""
preserved:
  meta: []
  hu: []
uncertainty: []
next_verification: []
```

## 可审计回答

用户要求查看过程、设计项目或验证 Skill 时，输出：

```yaml
B_T:
  task_goal: ""
  F_T:
    test_cases: []
  forbidden_loss: []
  epsilon_T:
    mode: qualitative | bounded | numeric
    value: null
  required_spaces: [meta, hu]
  optional_spaces: []
  output_contract: ""
  stop_condition: ""

M_T:
  retained_features: []
  removed_features: []
  loss_vector: []

H_T:
  direct: []
  composite: []
  path_residual: []
  flow_events: []
  retained_relations: []
  removed_relations: []

consistency:
  recoverable_from_M_T: []
  irreducible_in_H_T: []
  violations: []

attention:
  rho_state: low | medium | high
  theta_state: low | medium | high
  switch_reason: null

result:
  facts: []
  relations: []
  inferences: []
  gaps: []
  conflicts: []
  next_verification: []
```

只有存在可计算输入和已定义量纲时才填写精确数值。否则使用定性状态，不制造伪精度。

## 文件化状态

仅在用户要求持久化或任务需要跨轮次状态时创建：

```text
reference/source/
reference/store/
reference/read/
reference/flow/
reference/routing/
```

为每个节点保留来源指针。更新节点时记录替代关系，不覆盖源材料。`references/` 只包含 Skill 规范；不得写入任务状态。

## 证据边界

- 将原始观察、统计关联、计算扰动、机制推断和实验证据分开。
- 不把虚拟敲除、WGCNA、LASSO、随机森林或共表达结果写成因果证明。
- 不把框架内部的 ρ、θ、Ω、`θ'` 当作外部世界的测量值。
- 无来源时标记“待验证”，不要用完整叙事填平证据缺口。

## 停止条件

满足以下条件后停止继续扩展：

1. `F_T` 的测试项已通过；
2. `forbidden_loss` 无违反；
3. `M_T` 与 `H_T` 的跨空间差异在 `ε_T` 内；
4. 关键冲突已解决或显式保留；
5. 新增信息不再改变当前任务功能。
