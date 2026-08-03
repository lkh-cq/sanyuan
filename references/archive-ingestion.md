# 归档方案迁移协议

## 目的

归档对话中的方案不得直接混入冻结本体。它们必须先进入迁移队列, 经审查后再决定接入位置、状态和风险。

本协议用于把旧对话、草稿、审计意见和临时方案转为可追溯、可拒绝、可延后、可接线的项目条目。

## 迁移对象

~~~yaml
archive_item:
  id: archive_item_YYYYMMDD_NNN
  source_conversation: ""
  original_statement: ""
  normalized_summary: ""
  problem_it_solves: ""
  belongs_to:
    - ontology
    - reading_topology
    - modality_boundary
    - routing
    - storage
    - validation
    - domain_profile
  status: candidate | accepted | rejected | deferred
  integration_target: null
  risk_if_added: ""
  risk_if_omitted: ""
  authority_note: ""
~~~

## 状态定义

| 状态 | 含义 |
| --- | --- |
| candidate | 已识别, 尚未判断是否进入项目 |
| accepted | 接受为项目扩展或修订项 |
| rejected | 明确不纳入, 保留拒绝理由 |
| deferred | 有价值但当前接口、证据或工程条件不足 |

## 审查顺序

1. 保留用户原话与来源位置。
2. 判断该方案解决的问题。
3. 判断它属于本体、观测空间、路由、存储、验证还是领域 profile。
4. 检查是否违反 `architecture.md` 的当前冻结本体。
5. 检查是否已有现有模块可承载。
6. 记录加入风险与遗漏风险。
7. 决定状态与接入目标。

## 当前新增迁移项

~~~yaml
items:
  - id: archive_item_20260803_001
    normalized_summary: "三元语法是科研文本阅读拓扑方法, 不是写作生成器。"
    belongs_to: [reading_topology]
    status: accepted
    integration_target: references/reading-topology.md
    authority_note: "用户最新明确纠正高于旧版 sanyuan-syntax v0.3.0 表述。"

  - id: archive_item_20260803_002
    normalized_summary: "缺乏多模态环境时, 必须记录模态可见性边界。"
    belongs_to: [modality_boundary, validation]
    status: accepted
    integration_target: references/modality-boundary.md

  - id: archive_item_20260803_003
    normalized_summary: "阅读者/任务坐标会改变拓扑观测角度。"
    belongs_to: [reading_topology]
    status: accepted
    integration_target: references/reading-topology.md

  - id: archive_item_20260803_004
    normalized_summary: "证据压力用于记录节点承重, 不能只统计节点频次。"
    belongs_to: [reading_topology, validation]
    status: accepted
    integration_target: references/reading-topology.md

  - id: archive_item_20260803_005
    normalized_summary: "拓扑断裂与缺席节点是阅读判断的一部分。"
    belongs_to: [reading_topology, hu]
    status: accepted
    integration_target: references/reading-topology.md

  - id: archive_item_20260803_006
    normalized_summary: "图文互证需要分离正文声称与图表/补充材料证据。"
    belongs_to: [reading_topology, modality_boundary, hu]
    status: accepted
    integration_target: references/modality-boundary.md
~~~

## 入库原则

- 不得删除旧定义而不归档。
- 不得把旧对话中的想法直接升格为冻结本体。
- 用户最新明确表述可覆盖旧文件定位, 但必须记录覆盖关系。
- 工程未接线的方案只能标记为 candidate 或 deferred。
- 已接入项必须有明确文件、接口或验收位置。
