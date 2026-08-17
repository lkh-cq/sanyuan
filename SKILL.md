---
name: sanyuan-hive
description: "Use when 单任务多通道并行解算/分片调度/hive 隔离/多 worker 协同审查, 或用户提及 hive-main、B_T、boundary_hash、任务分片、MOA 相位、跨任务零耦合。sanyuan-hive 是以 hive_id + B_T 为唯一计算身份的单任务并行运行域; 不用于多聊天窗口记忆、不用于通用调度替代。"
version: 0.1.0a1
category: conscious
---

# sanyuan-hive — 单任务多通道并行解算运行域 (M1 骨架)

> 治理规范: Sanyuan_Hive_Main_技术指导与治理规范_v0.1 (P0/P1 已落地)
> 双主干: 本包独立于 main (orphan branch hive-main, 零共享历史, 禁 merge/rebase/cherry-pick)
> 状态: M1 骨架 — 合同+隔离语义+可安装空运行时; 调度/多 worker/MOA 为 M2-M4

## 一、符号定义

| 符号 | 定义 |
|------|------|
| hive_id | 单任务共享计算域的唯一身份; 禁 default、禁终端名推断 |
| B_T (boundary task) | 冻结的任务边界: task_goal + source_scope + stop_condition + forbidden_loss |
| boundary_hash | B_T canonical JSON 的 sha256; generation 内不可变 |
| generation | 任务代际; 目标改变必须升代或新建 hive |
| shard / worker / barrier | 可独立验收的计算分片 / 附着单 hive 的执行通道 / 收齐分片的同步点 |

## 二、核心方程 (规范 §5, alpha 工程默认值, 非本体常数)

```
boundary_hash = sha256(canonical_json(HASH_FIELDS))
γ_hat_i = 0.40·I_i + 0.25·F_i + 0.20·U_i + 0.15·R_i   (影响梯度)
c_ij = 0.35·D_ij + 0.25·S_ij + 0.25·O_ij + 0.15·T_ij  (耦合系数)
B_parallel = 1 - (T_split + max(T_i) + T_merge) / T_serial
```

## 三、使用边界 (MUST NOT)

1. 跨任务零默认耦合: 不同任务同域 = 上下文污染; 共享只经 import bridge (Owner 授权)。
2. 任一 worker 同一时刻只附着一个 hive; 一个 hive 只允许一个活动 B_T 代际。
3. hive_id / boundary_hash 不匹配 → fail-closed, 禁退化全局检索。
4. 外部副作用 (消息/推送/删除/不可逆动作) 必须过单独授权门, worker 永不直接执行。
5. 非多窗口记忆层、非 Obsidian/编辑器插件、非 K8s/Spark/MPI 替代品。

## 四、总线联系 (frozen core)

```
core_bundle: source=consciousness-bus, version=3.3.0, commit=875bda6
immutable: true, runtime_state_shared: false
```

ρ/θ 只描述收束与切换状态, 不代表正确率; S1 探索期 worker 禁预读他方结果, S2 只交换结构化结论。

## 五、入口

```
pip install -e .        # 可安装空运行时
hive --version          # → 0.1.0a1
schemas/                # boundary-task / worker-result (JSON Schema 2020-12)
tests/                  # P0 合同测试 (fail-closed)
```

## 六、里程碑

M0 边界冻结 ✓ → M1 orphan 基底 ✓ → M2 单 hive 闭环 → M3 多 worker → M4 MOA 相位 → M5 隔离硬化 → M6 多语言 → M7 校准 → M8 Alpha (hive-v0.1.0a1)
