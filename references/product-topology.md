# 产品拓扑（Product Topology）

> 权威登记：本文件是「四个 Router」名称、责任、仓库与版本的唯一登记表。
> 任何新增 Router 或改名/改仓/改版本，必须先更新本文件并登记到
> `references/project-manifest.yaml`，再走校验与发布。
> 本文件不重复登记项目版本号（版本唯一来源是 `project-manifest.yaml#project.version`）。

## 一、四个 Router 的职责边界

| 名称 | 责任 | 仓库 | 形态 | 版本来源 | 生命周期 |
| --- | --- | --- | --- | --- | --- |
| `consciousness-bus` | 认知预处理协议：任务边界、元/互归一化、藏归、注意力控制、读者端交付 | `lkh-cq/sanyuan`（本仓） | 核心 Skill | `project-manifest.yaml#project.version` | frozen/stable |
| `sanyuan-router` | 运行时链路总控：MCP 桥、8765 sidecar、路由表、Obsidian 插件健康检查与事故 runbook | `lkh-cq/sanyuan`（本仓 `extensions/sanyuan-router/`） | 嵌套扩展 Skill | 扩展包自身版本（独立演进） | experimental |
| `information-router` | 独立信息路由插件：来源通道、矛盾检索、长尾、引文链、版本链、偏差账本、学术协议 | `lkh-cq/information-router`（同族仓库） | 独立插件（skills-only） | 该仓库自身版本 | 独立演进 |
| `sanyuan-context-router` | Obsidian 桌面客户端：查询/选区 → 8765 sidecar → 预览/插入注入块 | `lkh-cq/sanyuan-context-router`（公开仓库） | Obsidian 插件（thin client） | 该仓库 manifest 版本 | 独立发布 |

边界规则：

- 四个 Router 互不冒充：`consciousness-bus` 管认知流程，`sanyuan-router` 管运行时链路，
  `information-router` 管外部检索证据链，`sanyuan-context-router` 管 Obsidian 宿主交互。
- `information-router` 与 `sanyuan-context-router` 是独立仓库，不把代码混入本仓；
  本 README 只把它们列为「同族项目 / sibling repository」。
- 本仓 `integrations/obsidian/` 只保留可复现源码；编译产物（`main.js`、`.egg-info`、
  `sidecar.env` 等）禁止提交，sidecar 与插件源码以独立发布为准。

## 二、Obsidian 依赖链契约

| 项 | 契约 |
| --- | --- |
| sidecar 发布 | 独立、带 tag 的发布；README 只引用不可变 commit/tag，不引用可变分支 |
| 客户端版本 | 固定兼容的 sidecar 版本（`sanyuan-obsidian` 0.1.0） |
| API 契约 | `GET /health`、`POST /v1/should-retrieve`、`POST /v1/retrieve-and-inject` |
| 健康检查 | 按契约版本判断功能，不假设命令在每一版都存在（如 `browse-sanyuan-nodes` 仅存在于上游 `integration/obsidian` 分支） |

## 三、Fullstack 状态

| 项 | 状态 |
| --- | --- |
| 本地实现 | `0.4.0a2`：61/61 测试通过、冻结核心 84 文件闭合、四模式与学术检索结构审计器可运行 |
| 建议归属仓库 | `lkh-cq/fullstack-academic`（2026-09-01 登记；创建被 GitHub 集成权限拒绝 403，授权已通过，需新会话重试创建） |
| 正式远端/仓库 | **未分配**（无 remote/upstream，正式 HEAD 仍为旧提交；仓库创建完成前不得视为已分配） |
| 计入已发布总包 | **否**。在分配正式仓库或远端并完成校验前，不得把 `0.4.0a2` 计入已发布总包 |
| 安装端 | 不得直接用新版本覆盖当前已加载版本；必须等校验通过后走正式升级流程 |

## 四、同族项目 / sibling repositories

- `lkh-cq/information-router`：独立信息路由插件（见上表）。
- `lkh-cq/sanyuan-context-router`：Obsidian 客户端（见上表）。
- `lkh-cq/mirror-bus`：跨窗口观察总线（mirror-bus-spec、soul-echo-spec 与运行时脚本）。

## 五、变更纪律

1. 新增/改名/改仓/改版本任何 Router，先改本文件，再改 manifest，再走校验。
2. 本仓校验器递归扫描 `extensions/` 与 `integrations/`：嵌套 `SKILL.md` 的 frontmatter
   只允许 `name` + `description`；禁止提交 `.egg-info`、无来源编译产物与 env 文件。
3. 发布与安装版本必须一致：GitHub main 的能力不得视为用户实际加载的能力，
   除非安装端已通过正式升级流程同步。

## 六、待办（用户侧操作，需新会话 / 管理员权限）

1. **创建 `lkh-cq/fullstack-academic` 仓库**：GitHub 集成授权已通过，需在新会话重试
   `create_repository`；创建后把 `0.4.0a2` 源码推入并打 tag，再更新本文件状态。
2. **安装端升级**：等主仓校验与发布 tag 通过后，走正式升级流程同步安装包；
   禁止直接用 GitHub main 的 `v3.3.6` 覆盖当前已加载版本。
3. **main 分支保护**：为 `lkh-cq/sanyuan` 的 main 开启分支保护与必需状态检查
   （`validate`、`endoscope-r` 为必需 check），需要仓库管理员权限。
