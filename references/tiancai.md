---
name: tiancai-extract
module_id: branch-sancai-tiancai
description: "天才提取: 规律/周期/阈值/稳定模式/变化规律/约束"
category: zang-gui
version: 0.3.0
canvas_refs:
  - assets/canvas/藏_三才.canvas
manifest_ref: references/project-manifest.yaml
---

# 天才_规律提取

> 天才 = 规律。不是"时空节律", 是客观规律。
> 覆盖: 周期、阈值、稳定模式、变化规律、约束。

---

## 提取协议

### 输入
任何信息片段。

### 提取问题
1. 这个信息以什么规律存在?
2. 有什么周期性(天文周期/生物周期/社会周期/技术周期)?
3. 有什么阈值或稳定模式?
4. 有什么变化规律?
5. 有什么约束条件(物理定律/制度约束/技术约束)?

### 输出格式

```yaml
tiancai:
  patterns:
    - <规律描述>
    - <周期描述>
  constraints:
    - <约束描述>
  timescale: <时间尺度>
```

### 提取示例

对象: 唐三彩钴蓝釉陶俑

```yaml
tiancai:
  patterns:
    - 钴离子在低温铅釉中的呈色规律
    - 二次烧成工艺规律(素烧+釉烧)
  constraints:
    - 窑温约束: 低温铅釉需~800-900°C
    - 钴矿产地约束: 唐代钴矿主要来自波斯
  timescale: 唐代(618-907CE), 钴蓝釉盛行于8-9世纪
```

### 边界

天才只记录规律本身, 不记录:
- 环境条件(属于地才)
- 实践行为(属于人才)
- 读取方式(属于地题)
- 抽象规律(属于归)

---

> 依赖: references/sancai-store.md, references/schema-store-node.schema.yaml
