---
name: meta-normalization
module_id: preprocessor-meta-normalization
description: "元信息空间独立归一化子skill。对信息的固有属性(三才层编码)进行任务条件化归一化。不依赖互归一化或任何核心skill, 可独立运行。输出M_T元信息任务视图。"
category: preprocessor
version: 0.1.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# 元信息空间归一化

> 独立子skill。只处理元信息空间, 不处理互信息空间。
> 输入: B_T(任务边界) + 原始信息材料
> 输出: M_T(元信息任务视图)

---

## 1. 冻结定义

### 元信息空间
对应信息的固有属性编码。映射三才层:
```
天才 = 规律 (周期/阈值/稳定模式/变化规律/约束)
地才 = 环境 (载体/空间/材料/制度/边界/保存条件)
人才 = 实践 (生产/行动/使用/实验/观察/记录)
```

元信息空间记录信息的静态属性, 无时间维度依赖。

### 三才是元信息的主编码器
三才藏提供元信息的主要存储坐标, 但不等于全部元信息理论。
元信息空间可以包含三才之外的属性轴(如来源标识、置信度), 但三才是默认轴。

### 与元信息空间的关系
元信息空间和互信息空间完全独立编码、独立归一化。
两者仅在跨空间一致性检查阶段通过 endpoint_refs 关联。
元归一化不知道互信息空间的存在, 也不需要知道。
元归一化和互归一化可以并行执行, 互不依赖。

---

## 2. 输入输出

### 输入
```yaml
input:
  B_T:                    # 任务边界(来自任务边界编译器)
    required_spaces: [...] # 必须包含 meta
    meta_axes: [...]      # 元信息轴选择
    forbidden_loss: [...]  # 禁止损失的元特征
    epsilon_T: 0.05       # 误差预算
  raw_material:            # 原始信息材料
    - id: "..."
      content: "..."
      store_node_refs: [...]  # 三才藏节点引用(可选)
```

### 输出
```yaml
meta_view:
  representation_id: "mt_{timestamp}_{seq}"
  boundary_id: "bt_..."       # 关联的任务边界ID
  observation_system: meta    # 固定为 meta
  origin: "..."               # 元空间原点描述
  axes:                       # 选择的轴
    - tiancai
    - dicai
    - rencai
  route_code: "q_M"           # 离散路由码(元卦)
  continuous_signal: "s_M"    # 连续信号分数
  source_node_refs:           # 三才藏节点引用
    - "store_tian_..."
    - "store_di_..."
    - "store_ren_..."
  preserved_features:         # 保留的元特征
    - "..."
  omitted_features:           # 被压缩删除的元特征
    - "..."
  recovery_refs:              # 恢复路径(被删特征的原始位置)
    - "..."
  loss:                       # 元信息损失向量
    structural: 0.02          # 结构损失
    functional: 0.01          # 功能损失
  valid: true                 # 是否通过功能检查
```

---

## 3. 归一化流程

### 步骤1: 轴加载
读取 B_T.meta_axes, 确定使用哪些三才轴。
默认全加载: [tiancai, dicai, rencai]
快速任务可以减少: 最少保留1轴。

### 步骤2: 元特征提取
对每个原始信息材料, 按选定的三才轴提取元特征:
- 天才轴: 提取规律、周期、阈值、约束
- 地才轴: 提取环境、载体、边界、保存条件
- 人才轴: 提取实践、实验、观察、记录方式

提取结果编码为 StoreNode 引用。

### 步骤3: 任务条件路由
对每个元特征, 根据B_T判定:
- required: 任务必需, 不能删除
- forbidden: 任务禁止(如错误信息源), 主动排除
- indifferent: 任务无关, 可删除

判定依据: forbidden_loss 列表 + F_T 功能测试。

### 步骤4: 任务条件压缩
对 indifferent 特征执行压缩:
- 保留: required 特征 + source_node_refs + recovery_refs
- 删除: indifferent 特征
- 记录: 被删特征的 recovery_refs(原始位置指针)

压缩约束: D_f(F_T(X), F_T(Z_T)) ≤ ε_T
- X: 压缩前信息
- Z_T: 压缩后信息
- D_f: 功能距离(不是向量距离, 不是方差距离)
- ε_T: 任务误差预算

如果压缩后功能损失超过ε_T, 恢复被删特征直到满足约束。

### 步骤5: 信号编码
生成连续信号 s_M 和离散路由码 q_M:
- s_M: 每个轴上的连续信号分数 [0, 1]
  - 1 = 信号强(该轴特征丰富)
  - 0 = 信号弱(该轴无特征)
- q_M: 三才信号组合的离散编码
  - 基于 s_M 的二值化(>threshold=1, <=threshold=0)
  - 三轴二值化 = 3位二进制 = 8种组合
  - 仅用于一级路由寻址, 不用于质量判断

### 步骤6: 功能检查
验证压缩后的元信息是否满足 F_T:
- 特征覆盖: required 特征是否全部保留
- 禁止损失: forbidden_loss 中的特征是否被删除
- 功能测试: F_T.test_cases 是否通过

通过 -> valid=true
未通过 -> 恢复被删特征, 重新检查, 直到通过或达到最大恢复次数

---

## 4. 秩自适应(修复原SVD缺陷)

原SVD归一化的缺陷:
- rank=2时 σ₃=0 导致 κ=σ₁/σ₃ 除零
- 无任务条件, 用全局方差代替任务功能
- 不区分元信息和互信息

本模块的修复:
- 不使用SVD作为过滤依据
- 不使用rank/κ/σ积作为阈值
- 使用任务条件化压缩(D_f ≤ ε_T)
- 元信息空间独立编码, 不与互信息混合

如果需要诊断元信息矩阵的结构(非门控), 可调用SVD作为诊断工具:
```
rank=2: κ₂ = σ₁ / max(σ₂, ε), V₂ = σ₁·σ₂
rank≥3: κ₃ = σ₁ / max(σ₃, ε), V₃ = σ₁·σ₂·σ₃
ε = 1e-8 (配置项)
```
但SVD诊断结果不作为过滤门控, 仅作为结构参考。

---

## 5. 独立性约束

本子skill:
- 不依赖互归一化
- 不依赖conscious/unconscious/deep-conscious
- 不依赖缓存波动力学
- 可独立运行, 只要输入 B_T + raw_material

本子skill不:
- 生成互信息(那是互归一化的工作)
- 执行跨空间一致性检查(那是多重归一化调度器的工作)
- 调用藏归调度器(那是配方的工作)
- 修改ρ/θ(那是核心层的工作)

---

## 6. 兼容包要求

- 输出格式: YAML + JSON兼容
- 可嵌入任何支持skill机制的环境
- 不依赖本地绝对路径
- 不依赖Hermes特定API
