# 三元语法阅读拓扑

## 定位

三元语法是一种科研文本阅读拓扑方法, 不是写作生成器。

它以已经存在的文本为输入, 读取作者实际如何组织信息, 并把文本中的行文功能、衔接、顺序、回环、证据承重、缺口和引用关系转写为可追溯、可比较、可统计的拓扑表示。

## 输入、操作、内部产物

~~~yaml
reading_topology:
  input:
    - published_text
    - abstract
    - section_text
    - figure_captions
    - tables_when_available
    - supplementary_text_when_available
  operation:
    - segment
    - identify_function
    - annotate_relation
    - record_order
    - record_loop
    - record_gap
    - bind_citation_or_evidence
  internal_working_artifacts:
    - observed_topology
    - evidence_pressure_map
    - topology_gap_map
    - absent_expected_node_map
~~~

这些产物用于工作层的追踪、比较和校验，不是默认交付格式。面向读者的分析必须继续经过 [reader-facing-analysis.md](reader-facing-analysis.md) 的自然语言转译。

## 双层接口

~~~yaml
delivery_interface:
  internal_reasoning:
    keeps:
      - node_and_edge_ids
      - relation_codes
      - evidence_pressure
      - topology_gaps
      - expected_but_absent
  reader_facing:
    requires:
      - readable_paragraphs
      - explicit_logical_relations
      - evidence_boundaries
      - necessary_limitations
    suppresses_by_default:
      - internal_ids
      - bare_arrows
      - schema_fields
      - unexplained_abbreviations
~~~

默认结果解释作者如何组织论述以及连接是否成立，不展示三元语法如何编码该结果。只有用户明确要求查看拓扑表示或审计记录时，才把内部产物作为独立附录提供。

## 禁止倒置

不得把阅读拓扑输出倒置为写作规定。

- 节点是对原文已经发生的行文功能的观测标签。
- 路径是对文本实际组织方式的描述。
- 频率、相邻转移和共现只能作为语料观察结果。
- "常见路径"只能是待验证经验假设, 不能成为强制模板。
- 不得把 slot package、compile_writing 或生成摘要作为三元语法核心目标。

## 阅读者与任务坐标

拓扑不是只存在于文本中, 也存在于文本与读取任务的耦合中。阅读前必须记录观察坐标。

~~~yaml
reader_task_coordinate:
  reader_profile:
    domain_background: []
    prior_knowledge: null
    trust_threshold: low | medium | high | unspecified
  reading_goal:
    type: reproduce | review | mechanism_search | flaw_detection | evidence_mapping | other
    question: ""
  reading_stage:
    stage: first_read | close_read | skeptical_read | re_read
    expected_topology: linear | looped | gap_focused | mixed
~~~

## 证据压力

证据压力记录一个节点在全文解释中承受的重量, 不是对真实性的直接裁判。

~~~yaml
evidence_pressure:
  node_ref: ""
  level: low | medium | high | critical
  reason: ""
  dependent_claims: []
  downgrade_reason: null
~~~

用法:

- low: 背景、定义、常规方法说明。
- medium: 局部承接、普通结果描述、次要解释。
- high: 支撑核心差异、关键机制、主结果。
- critical: 支撑全文结论、因果跳转、临床/应用外推。

## 拓扑断裂

拓扑断裂记录作者从 A 到 B 的连接残差。

~~~yaml
topology_gap:
  gap_id: ""
  from_node: ""
  to_node: ""
  missing_bridge: ""
  gap_type: causal | scale | species | method | evidence | concept | temporal | spatial
  severity: low | medium | high | critical
  visible_in_text: true
  affected_interpretation: ""
~~~

常见断裂包括:

- 相关性到因果机制。
- 体外结果到临床意义。
- 差异基因到功能通路。
- 表达变化到调控关系。
- 单细胞亚群到组织整体病理。
- 图表弱证据到正文强结论。

## 缺席节点

阅读拓扑必须记录应当出现但没有出现的证据节点。缺席节点不是空白, 而是读取记录的一部分。

~~~yaml
expected_but_absent:
  expected_node: ""
  reason_expected: ""
  domain_profile_ref: null
  impact_on_interpretation: low | medium | high | critical
  required_followup: ""
~~~

示例:

- 有表达差异但没有 rescue。
- 有通路富集但没有功能验证。
- 有细胞实验但没有组织验证。
- 有临床样本但没有混杂因素控制。
- 有 ferroptosis 结论但缺少核心验证链。

## 与当前冻结架构的关系

本模块属于补充观测空间与归档迁移层。它不修改三才、三题、互、FlowEvent、ρ/θ 或 n位聚焦的冻结定义。

三元语法的内部读取结果应优先写入运行时 `reference/read/` 与 `reference/flow/`, 不写入 Skill 的只读 `references/`。对用户的正式交付则按读者端分析规范生成连贯文字，不把运行时节点直接转印为正文。
