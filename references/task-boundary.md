---
name: task-boundary-compiler
module_id: preprocessor-task-boundary
description: "任务边界编译器: 在任何过滤/归一化之前执行。定义任务目标F_T、禁止损失、误差预算ε_T、必需观测空间、可选空间。不负责文档筛选, 不负责藏归写入。"
category: preprocessor
version: 0.1.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# 任务边界编译器

> 在任何过滤、归一化、藏归操作之前执行。
> 唯一职责: 把模糊的任务意图编译为可校验的边界条件。

---

## 1. 冻结定义

任务边界 B_T 是一个结构化对象, 包含:

```
B_T = {
  task_goal:        任务目标(自然语言)
  F_T:              任务功能(可验证的功能测试)
  forbidden_loss:   禁止损失(哪些特征/关系/路径不能被删除)
  epsilon_T:        误差预算(允许的最大功能损失)
  required_spaces:  必需观测空间(至少包含 meta + hu)
  optional_spaces:  可选观测空间(time/evidence/source/...)
  meta_axes:        元信息空间内部选择轴
  hu_axes:          互信息空间内部选择轴
}
```

约束:
- required_spaces 至少包含 meta 和 hu
- 禁止把 hu 从 required_spaces 中移除, 即使是快速任务
- epsilon_T > 0 (零误差预算意味着不压缩, 等于不做归一化)
- F_T 必须是可验证的, 不能是"质量好"这种不可测试语句

---

## 2. 编译流程

### 步骤1: 任务目标提取
输入: 用户的自然语言任务描述
输出: task_goal (一句话, 主谓宾结构)

### 步骤2: 任务功能定义
输入: task_goal
输出: F_T (功能测试函数描述)
规则: F_T 必须能回答"输入X, 任务应该输出什么"和"输入Z, 任务应该输出什么"

### 步骤3: 禁止损失识别
输入: task_goal + F_T
输出: forbidden_loss 列表
规则: 列出完成任务功能所必需、不能被压缩删除的特征/关系/路径

### 步骤4: 误差预算设定
输入: task_goal
输出: epsilon_T (浮点数, 范围 (0, 1])
默认值: 科研任务 0.05, 快速任务 0.2
规则: epsilon_T 越小, 压缩越保守

### 步骤5: 观测空间选择
输入: task_goal + F_T
输出: required_spaces + optional_spaces
规则:
- meta 和 hu 始终在 required_spaces 中
- 时间维度: 历史分析/时序比较任务 -> required; 其他 -> optional
- 证据维度: 文献综述/事实核查 -> required; 其他 -> optional
- 来源维度: 引用追溯 -> required; 其他 -> optional
- 不确定性维度: 风险评估 -> required; 其他 -> optional

### 步骤6: 轴选择
输入: required_spaces + optional_spaces
输出: meta_axes + hu_axes
规则:
- 元信息轴默认: 天才(规律), 地才(环境), 人才(实践)
- 互信息轴默认: 直接互, 复合互, 路径残差
- 快速任务可以减少轴数, 但不能减到零

---

## 3. 输出格式

```yaml
task_boundary:
  boundary_id: bt_{timestamp}_{seq}
  task_goal: "..."
  F_T:
    description: "..."
    test_cases:
      - input: "..."
        expected: "..."
  forbidden_loss:
    - "..."
  epsilon_T: 0.05
  required_spaces:
    - meta
    - hu
  optional_spaces:
    - time
    - evidence
  meta_axes:
    - tiancai
    - dicai
    - rencai
  hu_axes:
    - direct
    - composite
    - path_residual
```

---

## 4. 路由门: 任务复杂度判定

在编译完成后, 根据B_T的复杂度决定走哪条配方:

```
if required_spaces == [meta, hu] and optional_spaces == [] and epsilon_T >= 0.2:
    -> 快速信息筛选配方
else:
    -> 科研深度分析配方
```

快速配方的约束:
- 可以降低轴数量(最低: meta 1轴, hu 1轴)
- 可以降低关系展开深度(只保留直接互)
- 可以降低补充空间数量(全部optional)
- 可以使用粗粒度卦码
- 不能把互信息降为零
- 不能关闭元信息提取

---

## 5. 禁止行为

- 不负责文档筛选(那是归一化器的工作)
- 不负责藏归写入(那是藏归调度器的工作)
- 不负责ρ/θ控制(那是核心层的工作)
- 不生成任务结果(只生成边界条件)
- 不跳过元或互空间(即使任务看起来很简单)

---

## 6. 依赖

- 无核心层依赖(在ρ/θ之前运行)
- 输出 B_T 被以下模块消费:
  - 元归一化 (references/meta-normalization.md)
  - 互归一化 (references/hu-normalization.md)
  - 科研深度分析配方 (references/research-recipe.yaml)
  - 快速信息筛选配方 (references/fast-filter-recipe.yaml)
