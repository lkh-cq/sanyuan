# 输出契约

## 目录

1. 默认回答
2. 文献分析交付
3. 可审计回答
4. 文件化状态
5. 证据边界
6. 停止条件

## 默认回答

先回答用户实际问题。内部推理层负责保存节点、关系、路径和校验状态；读者交付层负责把它们转译为能独立阅读的自然语言。不要把三元三才术语当作装饰性前言，也不要把内部 Schema 当作结果。

默认交付必须：

- 使用完整概念名称和明确的逻辑连接词；
- 先给结论或分析主线，再展开必要依据；
- 主要逻辑分析使用连续段落；清单只承载真正并列的信息；
- 将事实、作者主张、分析者推断和证据缺口写成可区分的句子；
- 隐藏 `B_T`、`M_T`、`H_T`、`Z_T`、节点编号、关系代码、裸箭头和 YAML 账本；
- 仅在确有助益时使用表格或图，并补全名称、关系含义、来源和图例。

## 文献分析交付

文献精读、写作逻辑或证据拓扑分析按 [reader-facing-analysis.md](reader-facing-analysis.md) 输出。默认以 2—4 句的论述单元说明：

1. 作者先写什么、再写什么；
2. 该单元如何承接前文并把论述推进到哪里；
3. 关键证据支持到哪一步，是否存在跳跃或缺席节点。

不要把“节点—箭头—节点”或 `supports/contradicts` 等内部关系简写当作段落分析，也不要把每种逻辑关系机械拆成一个项目符号。示意图只能作为有完整注释的补充，不能替代自然语言解释。

## 可审计回答

只有用户明确要求查看过程、框架、机器表示或验证 Skill 时，才在主要结果之后追加独立审计块。可按任务裁剪以下结构，不要为了填满字段而制造内容：

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

审计块不能取代自然语言结果。只有存在可计算输入和已定义量纲时才填写精确数值；否则使用定性状态，不制造伪精度。

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
