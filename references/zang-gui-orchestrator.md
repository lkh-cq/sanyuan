---
name: zang-gui-orchestrator
module_id: branch-zang-gui
description: "藏归调度器: 确认任务是否需要藏归, 调用三才藏/三题归, 管理节点ID/路径/FlowEvent, 触发上下文编译, 回写执行结果。"
category: zang-gui
version: 0.3.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# 藏归调度器

> 只做调度, 不做定义。三才/三题/ρ/θ/deep-conscious的具体定义在各自模块中。

---

## 职责

1. 确认任务是否需要藏归
2. 调用三才藏(写入StoreNode)
3. 调用三题归(读取并生成ReadNode)
4. 管理节点ID
5. 管理路径(reference/store/, reference/read/)
6. 管理FlowEvent
7. 触发上下文编译(调用归/读取注入)
8. 回写执行结果

## 不得在调度器中复制

- 三才定义(在 references/sancai-store.md)
- 三题定义(在 references/santi-read.md)
- ρ/θ公式(在 references/rho-convergence.md 和 references/theta-switching.md)
- deep-conscious详细算法(在 references/n-focus.md)
- 具体领域提取模板(在 references/tiancai.md 等)
- 配方内容(在 references/research-recipe.yaml 和 references/fast-filter-recipe.yaml)

## 调度流程

```
任务输入
    |
    v
1. 路由判断: 需要藏归?
    |-- 否 -> 快速通道, 不执行藏归
    |-- 是 -> 继续
    |
    v
2. 三才藏: 调用 藏/天才_规律提取 + 藏/地才_环境提取 + 藏/人才_实践提取
   -> 生成 StoreNode -> 写入 reference/store/
    |
    v
3. FlowEvent: 记录天才->地才->人才的流止事件
   -> 写入 reference/flow/
    |
    v
4. 三题归: 调用 归/天题_本来样貌 + 归/地题_读取方式 + 归/人题_读取记录
   -> 生成 ReadNode -> 写入 reference/read/
    |
    v
5. 上下文编译: 调用 归/读取注入
   -> 按拓扑层级组织 -> 注入上下文
    |
    v
6. 回写: 执行结果回写, 新发现进入下一轮藏(生成新节点)
```

## 路由判断

任务满足以下任一条件时执行完整藏归:
- 涉及历史/设计/社会/环境/生产系统
- 多来源信息需要交叉验证
- 跨领域机制分析
- 高风险结论需要长期记录
- 需要区分原始信息与读取记录

否则走快速通道。

## ID管理

```
StoreNode: store_{layer}_{YYYYMMDD}_{seq}
ReadNode: read_{YYYYMMDD}_{seq}
FlowEvent: flow_{YYYYMMDD}_{seq}
CycleLink: cycle_{seq}
```

## 路径管理

```
reference/store/{store_id}.yaml   -- 藏节点
reference/read/{read_id}.yaml     -- 归节点
reference/flow/{flow_id}.yaml     -- 流止事件
reference/source/{source_id}.yaml -- 来源记录
reference/routing/                -- 路由表
```

运行时状态统一使用 `reference/`，禁止写入 Skill 的只读 `references/`。
使用相对路径，禁止绝对路径。

---

> 依赖: references/sancai-store.md, references/santi-read.md, references/flow-topology.md, references/schema-store-node.schema.yaml, references/schema-read-node.schema.yaml, references/schema-flow-event.schema.yaml, references/schema-cycle-link.schema.yaml
