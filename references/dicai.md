---
name: dicai-extract
module_id: branch-sancai-dicai
description: "地才提取: 环境/载体/空间/材料/制度/边界/保存条件"
category: zang-gui
version: 0.3.0
canvas_refs:
  - assets/canvas/藏_三才.canvas
manifest_ref: references/project-manifest.yaml
---

# 地才_环境提取

> 地才 = 环境。不是"地理物质条件", 是信息存在的环境。
> 覆盖: 环境、载体、空间、材料、制度、边界、保存条件。
> 地居天与人之间, 管理信息的流与止。地本身不携带固有方向。

---

## 提取协议

### 输入
任何信息片段。

### 提取问题
1. 这个信息在什么环境中被承载?
2. 载体是什么(物理载体/制度载体/数字载体/生物载体)?
3. 空间条件是什么(地理位置/生产空间/流通空间)?
4. 材料条件是什么(原材料/工具/能源)?
5. 制度条件是什么(法规/行规/习俗/技术标准)?
6. 边界在哪里(空间边界/时间边界/技术边界/制度边界)?
7. 保存条件是什么(保存方式/保存期限/保存风险)?

### 输出格式

```yaml
dicai:
  environment: <环境描述>
  carrier: <承载媒介>
  boundary: <边界描述>
  storage_condition: <保存条件/制度约束>
```

### 提取示例

对象: 唐三彩钴蓝釉陶俑

```yaml
dicai:
  environment: 唐代窑场环境, 丝路贸易通道
  carrier: 陶胎+低温铅釉, 物理载体
  boundary: 窑温800-900°C技术边界, 波斯钴矿供应边界
  storage_condition: 明器埋藏保存, 地下环境稳定
```

### 边界

地才只记录环境/载体/边界/保存条件, 不记录:
- 规律本身(属于天才)
- 实践行为(属于人才)
- 地本身不携带固有方向(方向只在FlowEvent中)

### 冻结约束

1. 不得把地固定解释为"地理物质条件"
2. 不得把地解释为"天和人的输出结果"
3. 不得把地画成自带方向的箭头
4. 地居天与人之间, 管理信息的流与止

---

> 依赖: references/sancai-store.md, references/schema-store-node.schema.yaml
