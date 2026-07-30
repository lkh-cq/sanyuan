---
name: hu-normalization
module_id: preprocessor-hu-normalization
description: "互信息空间独立归一化子skill。对信息之间的全部关系状态(直接互/复合互/路径残差/流止/转换/反馈)进行任务条件化归一化。不依赖元归一化或任何核心skill, 可独立运行。输出H_T互信息任务视图。"
category: preprocessor
version: 0.1.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# 互信息空间归一化

> 独立子skill。只处理互信息空间, 不处理元信息空间。
> 输入: B_T(任务边界) + 原始关系材料 + (可选)M_T元信息视图
> 输出: H_T(互信息任务视图)

---

## 1. 冻结定义

### 互信息空间
对应信息之间的全部关系状态编码。包括:
```
直接互:        A-B 直接关系
复合互:        A-B-C 经由中介
路径残差:      A-C直接 vs A-B-C复合 的差异
流止互:        天↔地↔人拓扑 flow/stop/filter 事件
转换互:        信息形态变化
反馈互:        输出回流影响输入
条件互:        特定条件下成立的关系
时序互:        随时间变化的关系
```

互信息空间记录信息的动态关系, 可带时间戳与事件ID。

### 与元信息空间的关系
互信息空间和元信息空间完全独立编码、独立归一化。
两者仅在跨空间一致性检查阶段通过 endpoint_refs 关联。
互归一化不需要等待元归一化完成, 可以并行执行。

### 互 ≠ FlowEvent
互是独立观测空间, FlowEvent只是互的一个子类型。
互归一化处理全部关系类型, 不限于流止事件。

---

## 2. 输入输出

### 输入
```yaml
input:
  B_T:                    # 任务边界
    required_spaces: [...] # 必须包含 hu
    hu_axes: [...]        # 互信息轴选择
    forbidden_loss: [...]  # 禁止损失的关系
    epsilon_T: 0.05       # 误差预算
  raw_relations:           # 原始关系材料
    - source: "..."
      target: "..."
      relation_type: "..."
      conditions: [...]
      strength: 0.8
  meta_view:               # (可选)元信息视图, 用于跨空间引用
    representation_id: "mt_..."
    source_node_refs: [...]
```

### 输出
```yaml
mutual_view:
  representation_id: "ht_{timestamp}_{seq}"
  boundary_id: "bt_..."
  observation_system: hu
  origin: "..."
  axes:                    # 选择的轴
    - direct
    - composite
    - path_residual
  route_code: "q_H"        # 离散路由码
  continuous_signal: "s_H" # 连续信号分数
  endpoint_refs:           # 关系端点引用
    - "store_..."
  relation_type: direct
  direct_or_composite: direct
  path_refs:               # 复合互的路径引用
    - "store_..."
  path_residual: null      # 路径残差
  conditions: []           # 关系成立条件
  strength: 0.8
  preserved_features:      # 保留的关系特征
    - "..."
  omitted_features:        # 被压缩删除的关系特征
    - "..."
  recovery_refs:           # 恢复路径
    - "..."
  residual_features:       # 路径残差特征(特殊保护)
    - "..."
  loss:
    structural: 0.02
    functional: 0.01
  valid: true
```

---

## 3. 归一化流程

### 步骤1: 轴加载
读取 B_T.hu_axes, 确定使用哪些互信息轴。
默认全加载: [direct, composite, path_residual]
快速任务可以减少: 最少保留1轴(至少保留direct)。

### 步骤2: 关系提取
对原始关系材料, 按选定的轴提取关系:
- 直接互轴: 提取 A-B 直接关系
- 复合互轴: 提取 A-B-C 经由中介的关系
- 路径残差轴: 计算 A-C直接 vs A-B-C复合 的差异
- 流止互轴: 提取 flow/stop/filter 事件(如有天地人拓扑上下文)
- 转换互轴: 提取信息形态变化
- 反馈互轴: 提取输出回流关系

提取结果编码为 MutualNode。

### 步骤3: 任务条件路由
对每个 MutualNode, 根据B_T判定:
- required: 任务必需的关系, 不能删除
- forbidden: 任务禁止的关系(如已知错误引用), 主动排除
- indifferent: 任务无关的关系, 可删除

判定依据: forbidden_loss 列表 + F_T 功能测试。

### 步骤4: 路径残差保护
路径残差是互信息空间的特殊特征:
- 如果 A-C 既有直接互又有复合互, 两者的差异(路径残差)必须保留
- 路径残差不能被当作 indifferent 删除
- 即使快速任务也必须保留路径残差(如果存在)

### 步骤5: 任务条件压缩
对 indifferent 关系执行压缩:
- 保留: required 关系 + path_residual + endpoint_refs + recovery_refs
- 删除: indifferent 关系
- 记录: 被删关系的 recovery_refs

压缩约束: D_f(F_T(X), F_T(Z_T)) ≤ ε_T
- 功能距离基于关系结构, 不是向量距离

### 步骤6: 信号编码
生成连续信号 s_H 和离散路由码 q_H:
- s_H: 每个轴上的连续信号分数 [0, 1]
  - 1 = 该轴关系丰富
  - 0 = 该轴无关系
- q_H: 轴信号二值化后的离散编码
  - 仅用于路由寻址, 不用于质量判断

### 步骤7: 功能检查
验证压缩后的互信息是否满足 F_T:
- 关系覆盖: required 关系是否全部保留
- 路径残差: 路径残差是否被保护
- 禁止损失: forbidden_loss 中的关系是否被删除
- 功能测试: F_T.test_cases 是否通过

通过 -> valid=true
未通过 -> 恢复被删关系, 重新检查

---

## 4. 独立性约束

本子skill:
- 不依赖元归一化(可以并行执行)
- 不依赖conscious/unconscious/deep-conscious
- 不依赖缓存波动力学
- 可独立运行, 只要输入 B_T + raw_relations

本子skill不:
- 生成元信息(那是元归一化的工作)
- 执行跨空间一致性检查(那是多重归一化调度器的工作)
- 调用藏归调度器
- 修改ρ/θ

---

## 5. 与元归一化的并行执行

元归一化和互归一化可以并行执行, 因为:
```
元归一化输入: B_T + raw_material (信息内容)
互归一化输入: B_T + raw_relations (信息关系)
```
两者的输入不同, 输出不同, 互不依赖。

跨空间一致性检查在两者都完成后执行:
```
比较:
  路线A: 完整元信息 -> 压缩元信息(M_T) -> 从M_T提取互(H'_T)
  路线B: 完整互信息 -> 压缩互信息(H_T)

若 |H'_T - H_T| > ε_T:
  说明元压缩删除了生成关系所需的对象特征
  或互压缩删除了无法由元信息恢复的关系特征
  -> 恢复被删特征
```

---

## 6. 兼容包要求

- 输出格式: YAML + JSON兼容
- 可嵌入任何支持skill机制的环境
- 不依赖本地绝对路径
- 不依赖Hermes特定API
