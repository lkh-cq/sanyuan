---
name: santi-read
module_id: branch-santi-read
description: "三题归: 信息流通方式, 形成抽象规律。天题=本来样貌, 地题=读取方式, 人题=读取记录。"
category: zang-gui
version: 0.3.0
canvas_refs:
  - assets/canvas/归_三题.canvas
manifest_ref: references/project-manifest.yaml
---

# 三题归 Skill

> 三题描述信息被读取时的流通和抽象结构。
> 三题属于"归"--信息的流通方式, 形成抽象规律。

---

## 一、冻结定义

```
天题 = 信息的本来样貌
地题 = 读取方式
人题 = 读取记录
```

| 题 | 含义 | 覆盖 |
|----|------|------|
| 天题 | 信息的本来样貌 | 信息在被解释前实际呈现的结构、状态、痕迹和可见规律 |
| 地题 | 读取方式 | 方法、路径、媒介、协议、工具、过滤条件 |
| 人题 | 读取记录 | 读取者形成的解释、摘要、模型、假说、争议和应用记录 |

三题处理的问题:

> 信息原本是什么, 通过什么方式被读取, 读取后留下什么记录, 并进一步形成何种抽象规律。

---

## 二、三才与三题的严格分界

| | 三才(藏) | 三题(归) |
|---|---------|---------|
| 天 | 天才=规律 | 天题=本来样貌 |
| 地 | 地才=环境 | 地题=读取方式 |
| 人 | 人才=实践 | 人题=读取记录 |
| 操作 | 储存具体内容 | 形成抽象规律 |
| 节点 | StoreNode | ReadNode |
| 不得 | 不得保存抽象规律 | 不得覆盖原始藏内容 |

**三元(天地人)是信息的本体结构, 三题是提取信息的命题手段。**
**三才(天才地才人才)是信息存储时的结构, 三题(天题地题人题)是信息读取时的结构。**
**藏归分离, 互不覆盖。**

---

## 三、三题提取协议

### 3.1 天题提取--信息的本来样貌

对藏节点, 提取其未被解释前的原始呈现:

```
天题_本来样貌:
  original_form: <信息在被解释前实际呈现的结构/状态/痕迹>
  observed_structure: <可见规律>
  unknowns: [未知/待解部分]
```

提取问题:
- 信息原本是什么(在解释之前)?
- 实际呈现什么结构?
- 有什么可见规律(未被解释的原始规律)?
- 什么是未知的?

### 3.2 地题提取--读取方式

对藏节点, 提取读取它使用的方式:

```
地题_读取方式:
  method: <读取方法>
  tool: <工具/媒介>
  path: <读取路径>
  filter: <过滤条件>
  scope: <读取范围>
  loss_risk: <信息损失风险>
```

提取问题:
- 通过什么方式读取(观察/实验/文献/数据挖掘)?
- 使用什么工具?
- 读取路径是什么?
- 有什么过滤条件(语言/年代/来源/置信度)?
- 读取范围是什么?
- 读取过程中有什么信息损失风险?

### 3.3 人题提取--读取记录

对藏节点, 提取读取后形成的记录:

```
人题_读取记录:
  reader: <读取者>
  reading_record: <读取形成的记录>
  interpretation: <解释>
  hypothesis: <假说>
  disagreement: <争议>
```

提取问题:
- 读取者是谁?
- 读取后形成了什么记录?
- 解释是什么?
- 有什么假说?
- 存在什么争议?

---

## 四、抽象规律

归产生抽象规律。这是归与藏的核心区别--藏保存具体内容, 归形成抽象规律。

```yaml
abstraction:
  derived_pattern: <推导出的抽象模式>
  applicability: <适用范围>
  limitations: <局限>
```

### 冻结约束

1. 归产生的读取记录不得直接覆盖原始藏内容
2. 归结论进入下一轮藏时, 必须生成新节点/新版本/明确的派生关系
3. 天题不是"规律层提问", 是"信息的本来样貌"
4. 地题不是"条件/边界层提问", 是"读取方式"
5. 人题不是"实践层提问", 是"读取记录"
6. 三题是归(读取)的三层结构, 不是藏(存储)的三层结构

---

## 五、输出格式

ReadNode 必须符合 `references/schema-read-node.schema.yaml`:

```yaml
read_id: <唯一ID>
source_store_ids: [引用的藏节点ID]

tianti:
  original_form: ...
  observed_structure: ...
  unknowns: [...]

diti:
  method: ...
  tool: ...
  path: ...
  filter: ...
  scope: ...
  loss_risk: ...

renti:
  reader: ...
  reading_record: ...
  interpretation: ...
  hypothesis: ...
  disagreement: ...

abstraction:
  derived_pattern: ...
  applicability: ...
  limitations: ...

provenance:
  source_files: [...]
  created_at: <ISO datetime>
  agent: <agent名称>
```

写入路径: `reference/read/{read_id}.yaml`

---

## 六、与其他模块的关系

| 模块 | 关系 |
|------|------|
| 三才藏 | 归读取藏节点。归结论进入下一轮藏时必须生成新节点 |
| 流止 | 天↔地↔人拓扑中的流止事件记录在FlowEvent中 |
| ρ收束 | conscious决定读取的宽度/窄度 |
| n位聚焦 | deep-conscious决定读取的bn位段 |

三题归不做最终价值和行动决策。判断由意识总线决定。

---

> 版本: 0.3.0 | 2026-07-27
> 来源: 三元道辩体系 v1.0 + V3冻结定义
> 依赖: references/schema-read-node.schema.yaml, references/sancai-store.md
