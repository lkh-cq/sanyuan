---
name: task-boundary-compiler
module_id: preprocessor-task-boundary
description: "任务边界编译器：定义当前子任务目标、功能、观测轴与注意力重点。B_T 不拥有过滤、压缩或删除权限；每个子任务的 FilterLease 默认 CLOSED。"
category: preprocessor
version: 0.2.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# 任务边界编译器

> 唯一职责：把模糊的任务意图编译为可校验的**当前子任务视图**。
>
> `B_T` 只决定“现在在做什么、应该重点看什么”，不决定“什么信息可以消失”。

## 1. 冻结候选约束

```text
B_T -> task/view/attention scope
B_T -/-> FilterLease
B_T -/-> source deletion
B_T -/-> lossy compression
```

任何旧实现若从 `B_T` 自动推导删除、HOLD、omitted 或压缩许可，属于 V3.4 迁移期禁止行为。

## 2. 结构

```text
B_T = {
  task_goal:              当前子任务目标
  F_T:                    可验证的前端功能
  preservation_requirements:
                          需特别强调保持可追溯的来源/关系/条件
  required_spaces:        必需观测空间
  optional_spaces:        可选补充空间
  meta_axes:              元信息对齐轴
  hu_axes:                关系对齐轴
  attention_focus:        主注意力与次级注意力提示
  output_target:          默认 RAGRequestFrame
}
```

### 不再属于 B_T 的字段

- `epsilon_T`：不得再作为默认有损压缩预算；
- `filter_permission`：过滤权限只能来自独立 FilterLease；
- `omitted/indifferent deletion policy`：不属于任务边界。

旧输入若仍携带 `epsilon_T`，前端必须忽略其“授权删除”含义，并记录兼容警告。

## 3. 编译流程

### 步骤 1：识别当前子任务

每个子任务都有独立 `task_id` 与 `boundary_id`。

复杂任务拆分后：

```text
Task
|- subtask_A -> B_T(A), FilterLease=CLOSED
|- subtask_B -> B_T(B), FilterLease=CLOSED
|- subtask_C -> B_T(C), FilterLease=CLOSED
```

过滤权限不得继承。

### 步骤 2：定义 task_goal

一句话描述当前子任务目标，不把“重点”翻译成“删除其它内容”。

例如：

```text
用户：总结导师录音里与 PNPLA8 实验有关的重点
```

合法编译：

```text
task_goal = 优先组织 PNPLA8 实验相关讨论
attention_focus.primary = PNPLA8 实验
```

禁止编译：

```text
remove_non_PNPLA8_discussion = true
```

除非用户另外显式开启该子任务的 FilterLease。

### 步骤 3：定义 F_T

F_T 只验证前端是否正确构造任务视图与下游请求，例如：

- primary query 是否反映用户目标；
- source refs 是否保持可追溯；
- required spaces 是否完成；
- ρ/θ 是否只作为 advisory hints；
- 无 FilterLease 时是否未发生 HOLD。

F_T 不把“压缩率高”当作成功指标。

### 步骤 4：preservation_requirements

默认原则是**全部 source refs 保持可追溯**。

该字段用于额外强调高风险信息，例如：

- 发言者；
- 时间顺序；
- 实验条件；
- 数值；
- 反对意见；
- 未解决问题；
- 证据来源。

它不是“只有列表中的内容才保留”。

### 步骤 5：观测空间选择

`meta` 和 `hu` 仍是默认必需空间；补充空间按任务选择。

选择观测轴只改变**前端展开与标注方式**，不允许因此丢失来源引用。

### 步骤 6：attention_focus

attention_focus 可包含：

```yaml
attention_focus:
  primary_axes: [...]
  secondary_axes: [...]
```

ρ/θ 可以据此给下游生成 attention hints，但不能操作 FilterLease。

## 4. 输出示例

```yaml
task_boundary:
  boundary_id: bt_20260819_001
  task_id: summarize_meeting_01
  task_goal: "优先组织导师讨论中与 PNPLA8 实验设计有关的内容"
  F_T:
    description: "生成保留来源可追溯性的 RAG 前端请求"
    test_cases:
      - input: "原始录音包含 PNPLA8 与其它实验讨论"
        expected: "全部来源片段仍可追溯；PNPLA8 进入 primary attention"
  preservation_requirements:
    - speaker_identity
    - temporal_order
    - experimental_conditions
    - disagreements
  required_spaces:
    - meta
    - hu
  optional_spaces:
    - time
    - source
  meta_axes:
    - tiancai
    - dicai
    - rencai
  hu_axes:
    - direct
    - composite
    - path_residual
  attention_focus:
    primary_axes:
      - PNPLA8
      - experiment_design
    secondary_axes:
      - unresolved_questions
  output_target: rag_request_frame
```

## 5. 路由

B_T 只可选择无损前端路径：

- `direct`：单一简单请求；
- `fast_view`：低成本、保真前端视图；
- `research_frontend`：多材料、多关系、深度前端编译。

大批次高过滤**不是 B_T 自动路由结果**。

若用户显式授权 FilterLease，调用器可以额外进入 `batch_filter` 路径；该路径的权限检查由 `filter-ratchet-permission.md` 负责。

## 6. 禁止行为

- 不得从 B_T 自动开启过滤；
- 不得从 task_goal 推导“非重点内容可删除”；
- 不得用 `epsilon_T` 赋予信息损失权限；
- 不得把快速任务等同于高过滤；
- 不得把 optional space 未展开解释为来源项可删除；
- 不得修改 ρ/θ；
- 不负责 embedding、retrieval、rerank 或 generation；
- 不生成最终 RAG 答案，默认输出前端请求合同。

## 7. 依赖与消费者

B_T 被以下模块消费：

- 元归一化；
- 互归一化；
- fast-view / research-front-end 配方；
- ρ/θ attention hint 编译器；
- RAGRequestFrame 编译器。

FilterLease 只引用 `task_id` / `boundary_id` 检查所有权，不由 B_T 创建。
