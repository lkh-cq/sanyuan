---
name: multiscale-reinjection-kernel
module_id: extension-multiscale-reinjection-kernel
description: "实验性 RAG 前端路由协议：用 SignalEnvelope 描述来源、时间尺度和传播提示，并把 rho/theta 仅作为 attention hints。不是 Transformer、RAG 或持久运行时。"
version: 0.2.0
category: experimental-frontend
manifest_ref: references/project-manifest.yaml
---

# 多时间尺度前端路由与语义再注入实验

## 0. 定位纠正

本模块原先被描述为“最小运行核”，容易把三元误解成自带状态循环、RAG、Transformer 或 Agent runtime。V3.4 起改为：

> **RAG 前端的实验性 routing metadata / request compilation 协议。**

它不拥有 retrieval、rerank、generation、向量库、长期状态引擎或用户信息生存权。

## 1. 核心对象不是 token，而是 FrontendEvent

前端只记录：

```text
FrontendEvent = payload_ref + routing_metadata
```

routing metadata 可以包含：

- source.kind；
- modality；
- temporal.timescale；
- temporal.persistence；
- propagation.scope；
- propagation.fanout；
- provenance；
- uncertainty；
- task_boundary_ref。

这些字段用于帮助下游 RAG 决定如何消费信息，不代表三元自己实现对应 attention。

## 2. 稠密/稀疏/broadcast 是提示，不是权限

`dense / sparse / broadcast` 只能作为 routing hint：

- dense：建议下游在当前局部工作集中保留较高连通；
- sparse：建议下游优先显式依赖/命中边；
- broadcast：建议下游把该状态视为较广域上下文。

它们不得：

- 删除 source refs；
- 自动触发 FilterLease；
- 变成“神经=稠密、代谢=稀疏”等固定生物学映射；
- 被三元解释为 learned attention 权重。

## 3. fast/slow 只描述时间尺度

`fast / intermediate / slow / static` 表示前端事件的更新时间尺度或持续性提示。

三元不拥有持久 `S_fast/S_slow` 世界状态。若下游系统具有 memory/state store，可自行选择如何解释这些字段。

因此：

```text
slow != persistent storage owned by Sanyuan
fast != automatic high-priority retrieval
```

## 4. rho/theta 的角色

`rho + theta = 1` 只作为主注意力辅助：

- rho：主方向收束提示；
- theta：次级/边界外关注提示。

允许写入 `RAGRequestFrame.attention_hints`。

禁止：

```text
rho/theta -> FilterLease
rho/theta -> source survival
rho/theta -> truth judgment
rho/theta -> retrieval execution
```

## 5. Normalization 与 routing metadata

SignalEnvelope 可以携带对齐后的术语、单位、来源和时间尺度元数据，但 normalization 必须遵守 `rag-frontend-governance.md`：

```text
representation may change
source survival may not change
```

无法对齐的内容标记 `unmapped/unresolved`，不进入默认 omitted。

## 6. ReinjectionFrame 的迁移含义

现有 `schema-reinjection-frame.schema.json` 暂时保留兼容，但其语义降级为**前端请求编译中间帧**，不是运行时世界状态。

允许字段：

```text
boundary_ref
new_event_refs
persistent_context_refs
attention_hints
routing_metadata_refs
```

其中 `persistent_context_refs` 只是外部/上游状态的引用，不代表三元自己维护长期 memory。

后续若 `RAGRequestFrame` 完全覆盖该需求，可将 ReinjectionFrame 标记 deprecated。

## 7. 与 FilterLease 的关系

无关系。

SignalEnvelope 的 source/timescale/fanout 不得自动转换为过滤条件。

只有 `filter-ratchet-permission.md` 定义的用户显式授权，才能建立 ACTIVE FilterLease。

## 8. 与已有仓库的边界

- **sanyuan**：定义前端语义与协议；
- **sanyuan-context-router**：薄客户端，可未来透传 RAGRequestFrame / SignalEnvelope；
- **visualR**：保持 PAL/九宫/矩阵参考语义，本模块不改；
- **java-runtime**：保持执行编排，不得因为本实验自动实现新的认知本体；
- **mirror-bus**：继续冻结，不恢复 watcher 或自动注入。

## 9. 参考实现边界

`scripts/multiscale_reinjection.py` 现阶段只能被视为协议实验夹具。

V3.4 必须审查并删除/降级任何以下行为：

- 自行维护长期世界状态；
- 把 rho/theta 当 gate 权限；
- 根据 fanout/timescale 删除来源；
- 自行执行 RAG；
- 自动恢复/压缩来源。

## 10. 晋升条件

本模块保持 experimental，至少满足：

1. RAGRequestFrame 前端合同稳定；
2. SignalEnvelope 不改变 source survival；
3. rho/theta 只作为 advisory hints；
4. 无任何路径可由 routing metadata 自动创建 FilterLease；
5. 与 context-router 透传测试通过；
6. 事故回放证明会议/录音/原始数据不会因任务聚焦静默丢失；
7. 再决定是否保留 ReinjectionFrame 或将其废弃。
