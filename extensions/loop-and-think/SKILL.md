---
name: loop-and-think
description: "Loop-and-think 迭代法——先动手，再根据反馈修改计划；循环思考与行动，不做一次性完备设计。触发：需求本身不确定、边做边决策、断点兼容、适用/不适用场景切换。"
version: 0.1.0
category: devops
---

# Loop and Think

> 状态：骨架（边做边填）
> 分支：feat/loop-and-think
> 定位：独立功能分支，待插入 sanyuan 架构 extensions/ 位置

## 核心循环

```text
先动手
  → 反馈（用户纠正 / 审计发现 / 代码交互）
  → 修改计划
  → 再动手
```

不做一次性完备设计。需求不确定时，先产出最小可验证的东西，再根据反馈收敛。

## 三条纪律

1. **先动手**：不纠结定义，先产出最小骨架。
2. **边做边决策**：遇到决策点当场判断，不停下来问大方案。
3. **断点兼容**：中途中断能续跑，开始需要的功能后续可退场。

## 当前实例（第一个应用）

hermes_memory 知识节点整理：

- 判定方式：孤立 ≠ 缺陷，先判 role/owner/lifecycle
- 硬门：`HERMES_MEMORY_GATE()`，判定未过禁止写动作
- TRAE 产物归类：reference/ 根 56 文件按类型归子目录 + 建索引
- 审计脚本：修 bug 三迭代，最终固化 maintenance/audit_orphan_nodes.py

## 待定义（边做边填）

- 与 conscious/unconscious 的接口
- 与 sanyuan 藏归/三元的对接点
- 何时用 loop-and-think、何时用一次性完备规划
