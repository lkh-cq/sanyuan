# 产品拓扑（Product Topology）

> 权威来源：本文件 + [`references/project-manifest.yaml`](project-manifest.yaml)。冻结定义只在此维护。
> 更新规则：任何 Router 的名称、责任、仓库或版本变更，必须先更新本文件与 manifest，再走发布校验。
> 版本规则：主 Skill 版本以 `project-manifest.yaml#project.version` 为唯一来源，本文件不重复登记；Router 版本为独立演进号。

## 总览

三元 Skill 总包由 1 个主 Skill 与 4 个 Router 组成。每个 Router 有唯一名称、唯一责任边界、唯一仓库（或待分配仓库）与独立版本号；任何两个 Router 不得互相冒充，也不得把另一个 Router 的能力当作自己的能力。

| 名称 | 责任边界 | 仓库 | 版本 | 生命周期 |
| --- | --- | --- | --- | --- |
| consciousness-bus | 认知流程预处理：任务边界、元/互归一化、藏归、ρ/θ 收束、读者端交付 | lkh-cq/sanyuan（根 Skill） | 见 manifest | stable（根） |
| extension-sanyuan-router | 运行时链路总控：MCP 桥、8765 sidecar、路由表派生、Obsidian 插件巡检与事故 runbook | lkh-cq/sanyuan `extensions/sanyuan-router` | 0.1.0 | experimental |
| sanyuan-context-router | Obsidian 桌面客户端（thin client）：检索请求、结果预览、插入/写回 | lkh-cq/sanyuan-context-router | 0.1.1 | 已发布（0.1.0/0.1.1） |
| information-router | 独立学术检索路由：来源通道、矛盾检索、证据归一、引文链、偏差账本 | lkh-cq/information-router | 0.1.0 | scaffold |
| fullstack-academic | 学术检索全链路：四模式检索 + 学术结构审计（Target/Theme/sub_n） | 待分配远端 | 0.4.0a2 | 未发布（本地工作区） |

## 责任边界（禁止互相冒充）

- **consciousness-bus** 管认知流程，不直接管运行时链路、不直接检索、不直接操作 Obsidian 插件。
- **extension-sanyuan-router** 管运行时链路（MCP 桥 / sidecar / 路由表 / 插件巡检），不替代认知流程，不替代学术检索。
- **sanyuan-context-router** 只做 Obsidian 客户端（thin client），检索/嵌入/重排/数据库都在独立 sidecar；客户端不得内置 sidecar 能力。
- **information-router** 是独立检索路由，代码不混入三元主仓；主仓只把它列为同族仓库。
- **fullstack-academic** 是学术检索全链路实现；在获得正式远端之前，不得计入已发布总包。

## 依赖与版本契约

| 依赖方 | 被依赖方 | 契约要求 | 当前状态 |
| --- | --- | --- | --- |
| sanyuan-context-router | sidecar（integration/obsidian） | 必须固定 tag/commit，不得依赖可变分支 | 已固定 commit `b930c8dd`（sanyuan-obsidian 0.1.0）；独立 tag 发布待办 |
| extension-sanyuan-router 健康检查 | sanyuan-context-router 客户端 | 按契约版本判断功能（如 browse-sanyuan-nodes） | 已按契约版本判定；0.1.1 无此命令，需该命令须从固定 commit 构建 |
| information-router | 学术检索 Schema / eval | 必须执行 JSON Schema、真实检索、来源验证 | 断裂：CI 仅做格式校验 |
| fullstack-academic | 正式远端 | 未分配 remote 前不发布 | 断裂：本地 0.4.0a2 无 remote |

## 发布与校验门

1. 主仓校验必须递归覆盖 `extensions/` 与 `integrations/`，禁止提交 `.egg-info` 与无来源的编译产物。
2. 安装端升级必须在本文件所列校验全部通过后进行；不得直接用最新 main 覆盖运行中的安装包。
3. 每个 Router 的发布必须携带固定版本标识（tag 或 commit），并能在健康检查中按契约版本自证。
4. 任何 Router 的版本漂移都必须记录在 `version-provenance.md`。
