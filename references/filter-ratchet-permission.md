---
name: filter-ratchet-permission
module_id: preprocessor-filter-ratchet
version: 0.1.0
description: "大批次高过滤任务的一次性手动权限协议。Filter 只执行被冻结的机械条件，不生成条件、不做判断、不继承权限。"
category: preprocessor-permission
manifest_ref: references/project-manifest.yaml
---

# FilterLease：单任务棘轮过滤权限

## 1. 目标

FilterLease 用来解决一个单一问题：**什么时候允许前端把部分来源引用暂不送入本次下游 RAG 请求。**

它不是注意力、不是任务边界、不是归一化、不是判断器。

默认：

```text
FilterLease = CLOSED
```

## 2. 激活条件

只有以下条件同时成立，FilterLease 才可从 ARMED 进入 ACTIVE：

```text
user_explicit_authorization = true
AND owner_task_id == current_subtask_id
AND batch_mode == large_batch
AND requested_filter_intensity == high
AND filter_spec_frozen == true
```

任一条件不满足：

```text
FilterLease = CLOSED or ARMED
filter execution = forbidden
```

其中“large_batch”由调用侧/适配器依据该数据类型的批处理配置判定，但**不能单独授予权限**；“high”必须来自用户的明确请求或用户主动选择的高过滤模板。

## 3. 状态机

```text
CLOSED
  |
  | user explicit authorization for one subtask
  v
ARMED(task_id)
  |
  | large_batch + high_filter + frozen_spec
  v
ACTIVE(task_id)
  |
  | complete | abort | timeout | boundary_change | spec_change
  v
SEALED
```

约束：

- `SEALED` 是终态；
- `SEALED -> ACTIVE` 禁止；
- `ACTIVE -> ARMED` 禁止；
- 重新过滤必须创建新 `lease_id`；
- Agent 不能自行执行 `CLOSED -> ARMED`。

## 4. 单授权线程

“单线程”指**权限所有权单一**，不是限制 CPU 只能串行计算。

一个 ACTIVE lease 可以被多个并行 worker 消费：

```text
FilterLease(task_A)
   -> worker_1
   -> worker_2
   -> worker_3
```

但 worker 不得：

- 创建子 lease；
- 复制 lease 给其它任务；
- 修改 filter spec；
- 延长 lease；
- 改变 lease owner；
- 将 lease 从 SEALED 恢复。

## 5. 权限不继承

任务树中的每个子任务初始化：

```text
FilterLease = CLOSED
```

例如：

```text
Task
|- A: 大批次 DEG 过滤       -> ACTIVE(A)
|- B: 机制解释               -> CLOSED
|- C: 会议录音总结           -> CLOSED
```

即使 A 再拆成 A1 / A2，也不能把 A 的权限自动传给 A1/A2。

冻结原则：

```text
result can propagate
permission cannot propagate
```

## 6. FilterSpec

FilterSpec 必须在 ACTIVE 前冻结。

允许的 filter 条件必须是可执行、可复现的字段/标签/阈值规则，例如：

```text
FDR < 0.05
AND abs(logFC) > 1
```

或：

```text
speaker_role == "mentor"
AND label == "explicit_action_item"
```

其中 `label` 必须在过滤前由独立标注过程产生；Filter 本身不能决定一句话是否“重要”“有价值”“相关”“可信”。

禁止的 FilterSpec：

```text
keep biologically important items
keep useful discussion
remove irrelevant ideas
keep high-value evidence
```

这些条件需要判断，不属于 Filter 权限。

## 7. PASS / HOLD，不修改来源

Filter 只产生：

```text
PASS -> 进入本次 RAG candidate refs
HOLD -> 本次不送入 candidate refs
```

HOLD 不等于删除。

来源材料、原始引用与原始关系不可由 Filter 修改。

## 8. FilterReceipt

每次 ACTIVE lease 结束必须生成 receipt：

```yaml
filter_receipt:
  lease_id: fl_...
  task_id: ...
  authorization: user_explicit
  batch_mode: large_batch
  filter_intensity: high
  spec_hash: ...
  passed_count: ...
  held_count: ...
  source_mutated: false
  final_state: SEALED
```

该 receipt 用于防止静默降级和后续审计，不赋予下一任务任何权限。

## 9. 与 ρ/θ 的隔离

`ρ + θ = 1` 只能辅助当前主注意力。

禁止：

```text
rho high -> enable filter
rho low -> widen filter
θ high -> revive FilterLease
θ low -> seal or modify filter
```

FilterLease 状态不接受 ρ/θ 写入。

## 10. 与 B_T 的隔离

`B_T` 可以描述子任务目标、重点和观测范围，但不能包含“自动允许删除”的隐式权限。

如果 B_T 改变：

```text
ACTIVE -> SEALED
```

新 B_T 若仍需过滤，用户必须重新授权一个新 lease。

## 11. 失败策略

以下情况全部 fail closed：

- 未识别到明确授权；
- 授权范围与 current task_id 不一致；
- 任务不是大批次；
- 过滤强度未明确为 high；
- FilterSpec 仍在变化；
- FilterSpec 含模糊语义判断；
- 并行 worker 请求扩权；
- 原 lease 已 SEALED。

fail closed 时可继续排序、标记、归一化、查询编译，但不得 HOLD 来源项。
