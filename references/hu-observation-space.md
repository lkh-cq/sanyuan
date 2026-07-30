---
name: hu-observation-space
module_id: observation-hu
description: "互信息空间主模块。互=独立关系观测空间, 非FlowEvent, 非信息论mutual information。FlowEvent⊂互。互记录信息之间的直接互、复合互、路径残差、流止、转换、反馈等全部关系状态。"
category: observation-space
version: 0.1.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# 互信息空间

> 互 = 独立关系观测空间
> FlowEvent ⊂ 互
> 互 ≠ 信息论中的 mutual information

---

## 1. 冻结定义

### 互是什么

互是独立于元信息的关系观测空间。它记录信息之间的全部关系状态。

```
互 = 独立关系观测空间

互可以记录:
  直接互:        A-B 之间的直接关系
  复合互:        A-B-C 经由中介的关系
  路径残差:      A-B-C 与 A-C 的路径差异
  流止互:        天↔地↔人拓扑中的 flow/stop/filter 事件
  转换互:        信息从一种形态变为另一种
  反馈互:        输出回流影响输入
  条件互:        在特定条件下才成立的关系
  时序互:        随时间变化的关系
  观测互:        观测行为本身对信息的影响
  任务互:        任务上下文产生的关系
```

### FlowEvent 的位置

```
FlowEvent ⊂ 互

FlowEvent = 互空间中专门记录天↔地↔人拓扑中
            flow/stop/filter/transform/buffer/feedback
            等运行过程的一种事件表示
```

FlowEvent 不是互的全部。互还包括不依赖天地人拓扑的关系(如两个文献之间的引用关系)。

### 互不是什么

- 互不是元信息的附属字段(互是独立观测空间)
- 互不是信息论中的 mutual information(避免术语混淆, 机器ID用hu不用mutual-information)
- 互不是第四个本体实体(互是观测空间, 不是天地人之外的第四个"才")
- 互不是"耦合界面"的另一种说法(互有独立的轴、原点和编码)

---

## 2. 互空间结构

### 原点
```
原点: 无可观测关系 / 关系基线
```
当两个信息之间没有可观测的关系时, 互空间处于原点状态。

### 轴
```
默认轴:
  方向:     关系的方向性(单向/双向/无向)
  条件:     关系成立的条件
  强度:     关系的强度
  时序:     关系的时间特征
  流止:     flow/stop状态(仅FlowEvent子类型)
  转换:     信息形态变化
  损失:     关系传递中的信息损失
  可逆性:   关系是否可逆
```

### 编码
```
连续信号: s_H (每个轴上的连续分数 [0,1])
离散路由码: q_H (轴信号二值化后的离散编码)
```

连续信号用于边界判定、置信度计算和重算。
离散路由码用于快速路由和查表。
两者都不用于质量判断或真实性判断。

---

## 3. 互节点(MutualNode)

互空间的基本单元是 MutualNode, 不是 StoreNode。

MutualNode 描述两个或多个信息节点之间的关系:

```yaml
mutual_node:
  mutual_id: "hu_{timestamp}_{seq}"
  endpoint_refs:           # 关系端点(2个或更多)
    - "store_tian_..."
    - "store_ren_..."
  observation_system: hu
  relation_type: direct    # direct/composite/flow_event/transform/feedback/...
  direct_or_composite: direct
  path:                    # 复合互的路径
    - "store_tian_..."
    - "store_di_..."       # 中介
    - "store_ren_..."
  path_residual: null      # 路径残差(如果A-C直接互与A-B-C复合互不同)
  conditions: []           # 关系成立条件
  strength: 0.8            # 关系强度
  timestamp: "..."         # 时序(可选)
  via_role: null           # 仅FlowEvent子类型强制为di
```

### via_role 约束
`via_role` 只在 FlowEvent 子类型中强制为 `di`(地居中)。
一般 MutualNode 的 via_role 为 null 或指定其他中介角色。

---

## 4. 与元信息空间的关系

```
元信息空间 (M):              互信息空间 (H):
  原点: 坤(未观测)            原点: 无可观测关系
  轴: 天才/地才/人才          轴: 方向/条件/强度/时序/...
  编码: 三才层编码            编码: 关系层编码
  记录: 信息的静态属性        记录: 信息之间的动态关系
  无时间维度依赖              可带时间戳
```

两者完全独立编码、独立归一化。
仅在跨空间一致性检查阶段通过 endpoint_refs 关联。

关联方式: MutualNode.endpoint_refs 引用 StoreNode.store_id。
不是把互作为 StoreNode 的一个字段。

---

## 5. 直接互 vs 复合互

### 直接互
```
A --- B
```
A 和 B 之间有直接关系, 无中介。
例: 文献A直接引用文献B。

### 复合互
```
A --- B --- C
```
A 和 C 之间的关系经由 B 中介。
例: 文献A引用文献B, 文献B引用文献C。A和C的关系是复合互。

### 路径残差
```
A --- C (直接互)
A --- B --- C (复合互)
```
如果 A-C 既有直接互又有复合互, 两者的差异就是路径残差。
路径残差 ≠ 0 说明直接关系和经由中介的关系不完全等价。
路径残差是互信息空间的重要特征, 不能被压缩删除。

---

## 6. 模块文件结构

```
互/
├── SKILL.md              # 本文件(互空间主模块)
└── (子模块待扩展)
```

当前版本只建主模块。直接互、复合互、互变换、互压缩等子模块待有实际使用经验后扩展。

---

## 7. 独立性约束

本模块:
- 不依赖元归一化
- 不依赖conscious/unconscious/deep-conscious
- 定义互空间的结构和编码, 不执行归一化(那是互归一化子skill的工作)

---

## 8. 术语防护

- 机器ID: hu-observation-space (不用 mutual-information)
- 中文名: 互信息空间 / 互
- 禁止将互称为"信息论互信息"
- 禁止将互降格为FlowEvent
- 禁止将互作为StoreNode的字段
