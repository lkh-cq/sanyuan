---
name: rencai-extract
module_id: branch-sancai-rencai
description: "人才提取: 生产/行动/使用/实验/观察/记录等实践"
category: zang-gui
version: 0.3.0
canvas_refs:
  - assets/canvas/藏_三才.canvas
manifest_ref: references/project-manifest.yaml
---

# 人才_实践提取

> 人才 = 实践。不是"社会身份/需求", 是留下记录的实践行为。
> 覆盖: 生产、行动、使用、实验、观察、记录等实践。

---

## 提取协议

### 输入
任何信息片段。

### 提取问题
1. 由什么实践留下具体记录?
2. 行动者是谁(生产者/使用者/观察者/记录者)?
3. 实践行为是什么?
   - 生产实践: 制造、开采、加工、建造
   - 使用实践: 消费、应用、操作
   - 实验实践: 试验、测量、验证
   - 观察实践: 观测、调查、记录
   - 记录实践: 书写、绘制、编码、存档
4. 记录行为是什么(如何留下具体记录)?
5. 实践的边界在哪里(谁能做/在哪里做/何时做)?

### 输出格式

```yaml
rencai:
  actors: [行动者]
  practices: [实践行为]
  recording_action: <留下记录的具体行为>
```

### 提取示例

对象: 唐三彩钴蓝釉陶俑

```yaml
rencai:
  actors:
    - 胡商(钴矿原料输入者)
    - 窑匠(陶俑制造者)
    - 贵族(明器消费者)
  practices:
    - 钴矿开采与贸易
    - 釉料制备与施釉
    - 素烧与釉烧
    - 明器采购与随葬
  recording_action: 陶俑烧制成品本身即为记录, 釉色/胎体/纹样保存了工艺信息
```

### 边界

人才只记录实践行为, 不记录:
- 规律本身(属于天才)
- 环境条件(属于地才)
- 读取方式(属于地题)
- 抽象规律(属于归)

### 冻结约束

1. 不得把人才固定解释为"社会身份/需求"
2. 人才记录的是实践行为, 不是身份标签
3. 人才不判断实践的价值(判断由意识总线决定)

---

> 依赖: references/sancai-store.md, references/schema-store-node.schema.yaml
