# 决策记录 0001 — hive-main 独立身份与不可变合同

- 日期: 2026-08-16
- 规范: Sanyuan_Hive_Main_技术指导与治理规范_v0.1 (P0 边界冻结产物)
- 状态: 已采纳

## 裁决

hive-main 不是聊天记忆分支，也不是 main 的功能开关。它是以 hive_id + B_T 为唯一计算身份的单任务、多通道并行解算运行域；窗口仅作为 worker 入口。

## 不可变合同

1. 一个 hive 只允许一个活动 B_T 代际; 任一 worker 同一时刻只能附着一个 hive。
2. 任务目标改变必须创建新 hive 或显式升代 (boundary generation)。
3. 跨任务零默认耦合; 共享实现只能经 frozen core bundle (只读、带 sha256 指纹) 导入。
4. 任何 hive_id / boundary_hash 不匹配必须 fail-closed, 不得退化为全局检索。
5. 外部副作用必须经单独授权门; worker 永不直接执行不可逆动作。

## 非目标 (MUST NOT)

- 不作为多个无关聊天窗口的自动记忆层或全局人格层。
- 不作为 Obsidian/Markdown/终端/编辑器的绑定插件。
- 不宣称替代 Kubernetes/Ray/Spark/MPI。
- 不执行持续模型训练、权重自动回写或跨任务隐式迁移。
