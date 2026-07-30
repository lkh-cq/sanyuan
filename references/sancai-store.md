---
name: sancai-store
module_id: branch-sancai-store
description: "三才藏: 信息储存方式。天才=规律, 地才=环境, 人才=实践。保存具体内容, 不保存抽象规律。"
category: zang-gui
version: 0.3.0
canvas_refs:
  - assets/canvas/藏_三才.canvas
manifest_ref: references/project-manifest.yaml
---

# 三才藏 Skill

> 三才描述信息被保存时的具体存在结构。
> 三才属于"藏"--信息的储存方式, 保存具体内容。

---

## 一、冻结定义

```
天才 = 规律
地才 = 环境
人才 = 实践
```

| 才 | 含义 | 覆盖 |
|----|------|------|
| 天才 | 规律 | 周期、阈值、稳定模式、变化规律、约束 |
| 地才 | 环境 | 环境、载体、空间、材料、制度、边界、保存条件 |
| 人才 | 实践 | 生产、行动、使用、实验、观察、记录等实践 |

三才处理的问题:

> 信息以什么规律存在, 在什么环境中被承载, 由什么实践留下具体记录。

---

## 二、与旧定义的冲突处理

| 旧定义 | 冻结定义 | 处理 |
|--------|---------|------|
| 天=时空节律 | 天=规律 | 旧定义窄化。时空节律只是规律的一种。迁入archive |
| 地=地理物质条件 | 地=环境 | 旧定义窄化。地理物质只是环境的一种。迁入archive |
| 人=社会身份/需求 | 人=实践 | 旧定义窄化。社会身份只是实践主体的一种。迁入archive |
| 天×人->地 | 天↔地↔人拓扑 | 旧定义把地当作天人耦合的输出。冻结定义: 地居中, 管理流止。迁入archive |
| 六个耦合界面 | FlowEvent | 旧定义的六个耦合界面重新解释为FlowEvent。迁入archive |

---

## 三、三才提取协议

### 3.1 天才提取

对输入信息, 提取其规律层:

```
天才_规律:
  patterns: [规律/周期/阈值/稳定模式]
  constraints: [变化规律/约束]
  timescale: <时间尺度>
```

提取问题:
- 这个信息以什么规律存在?
- 有什么周期性?
- 有什么阈值或稳定模式?
- 有什么约束条件?

### 3.2 地才提取

对输入信息, 提取其环境层:

```
地才_环境:
  environment: <环境/载体/空间>
  carrier: <承载媒介>
  boundary: <边界/保存条件>
  storage_condition: <制度约束>
```

提取问题:
- 这个信息在什么环境中被承载?
- 载体是什么(物理载体/制度载体/数字载体)?
- 边界在哪里?
- 保存条件是什么?

### 3.3 人才提取

对输入信息, 提取其实践层:

```
人才_实践:
  actors: [行动者]
  practices: [生产/行动/使用/实验/观察/记录]
  recording_action: <留下记录的具体行为>
```

提取问题:
- 由什么实践留下具体记录?
- 行动者是谁?
- 实践行为是什么(生产/使用/实验/观察)?
- 记录行为是什么?

---

## 四、写入规范

### 4.1 StoreNode 格式

三才藏写入的节点必须符合 `references/schema-store-node.schema.yaml`:

```yaml
store_id: <唯一ID>
source_id: <来源ID>
title: <标题>

tiancai:
  patterns: [...]
  constraints: [...]
  timescale: ...

dicai:
  environment: ...
  carrier: ...
  boundary: ...
  storage_condition: ...

rencai:
  actors: [...]
  practices: [...]
  recording_action: ...

concrete_content: <具体内容>
source_anchor: <来源锚点>
evidence_type: excavation | text | experiment | user_input | observation | literature
confidence: 0.0-1.0
disputed: false
version: <版本号>
```

### 4.2 写入路径

```
reference/store/{store_id}.yaml
```

### 4.3 约束

1. 藏保存具体内容, 不保存抽象规律(抽象属于归)
2. 不得把地固定解释为地理物质
3. 不得把天才固定解释为时空节律
4. 不得把人才固定解释为社会身份
5. 不得使用天×人->地作为基础本体
6. 写入后必须读回验证(铁律1)
7. 使用相对路径, 禁止绝对路径

---

## 五、与其他模块的关系

| 模块 | 关系 |
|------|------|
| 三题归 | 归读取藏节点, 产生抽象规律。归结论进入下一轮藏时必须生成新节点 |
| 流止 | 天↔地↔人拓扑中的流止事件记录在FlowEvent中 |
| ρ收束 | conscious决定提取的宽度/窄度 |
| n位聚焦 | deep-conscious决定提取的bn位段 |

三才藏不做判断。判断由意识总线决定。
三才藏不决定宽度/窄度。宽度/窄度由conscious决定。
三才藏不决定粒度。粒度由拓扑层级决定。

---

> 版本: 0.3.0 | 2026-07-27
> 来源: 三元道辩体系 v1.0 + V3冻结定义
> 依赖: references/schema-store-node.schema.yaml
