---
name: sanyuan-router
description: "Use when 调用/修复/巡检 sanyuan 意识总线运行时链路 (MCP桥/8765 sidecar/路由表/Obsidian插件). 三元router总控: 一条命令健康检查, 全链路拓扑图, 事故runbook."
---

# Sanyuan Router — 意识总线运行时链路总控

> 模块: extension-sanyuan-router
> 版本: 0.1.0 (experimental)
> 分类: devops
> 来源: 2026-08-25 obsidian-memory 全链路修复战役 (mcp 2.0 升级断桥事故 + sidecar 路由接入 + 插件 0.2.0)
> 定位: consciousness-bus 管"认知流程", 本模块管"运行时链路"——认知总线的物理血管。归一化端口(sanyuan-normalization-port)是数据平面, 本模块是控制平面。

## 一、触发条件

- `sanyuan router` / `链路检查` / `链路挂了` / `MCP 修` / `sidecar` / `插件更新`
- 任何 vault 工具 / 8765 端口 / bridge 路由表相关故障
- hermes-agent 升级后 (高发事故窗口, 见 §五 runbook)

## 二、全链路拓扑 (2026-08-25 实测版)

```
┌─ 认知层 ──────────────────────────────────────────────┐
│ consciousness-bus (流程) ←→ 本模块 (链路)              │
└──────────────────────────────────────────────────────┘
                    │
┌─ L1-L3: MCP 桥 (Hermes→vault, stdio) ─────────────────┐
│ 解释器: ~/.hermes/mcp_servers/mcp1x-venv (mcp==1.28.1) │
│   L1 obsidian-memory.py   6工具: vault_search/read/    │
│      write/context/status/index  → FTS5 DB             │
│   L2 playwright_bridge.py 5工具: navigate/snapshot/    │
│      screenshot/click/get_html   → chromium headless   │
│   L3 shellbox.py          2工具: run_command/          │
│      get_file_info               → subprocess          │
│ ⚠ 三桥与 hermes 本体 venv (mcp 2.0) 解耦, 禁回迁       │
└──────────────────────────────────────────────────────┘
                    │
┌─ L4: sidecar (Obsidian插件→HTTP:8765) ────────────────┐
│ 源: sanyuan仓 integration/obsidian 分支                │
│   → integrations/obsidian/python (stdlib-only)         │
│ 启动: bash ~/.hermes/mcp_servers/start_sanyuan_sidecar.sh│
│ 端点: GET /health | POST /v1/retrieve-and-inject       │
│ 路由: SANYUAN_ROUTING_TABLE → bridge/sidecar_routes.yaml│
│   (由 maintenance/gen_sidecar_routes.py 从冻结 bridge  │
│    表派生; bridge 表更新后必须重跑生成器)               │
└──────────────────────────────────────────────────────┘
                    │
┌─ L5-L9 ───────────────────────────────────────────────┐
│ L5 context.json 注入桥 (Obsidian→Hermes, 插件侧写)     │
│ L6 mirror bus  ~/.hermes/mirror/ (跨窗口)              │
│ L7 soul_echo.jsonl (注意力回写)                        │
│ L8 trae_bridge.py (Trae 桥)                            │
│ L9 bridge/topology_routing_table.yaml (冻结, 只读)     │
└──────────────────────────────────────────────────────┘
```

## 三、一条命令健康检查

```bash
python3 ~/.hermes/skills/devops/sanyuan-router/scripts/router_health.py
```

输出: 每条线路 PASS/FAIL + 修复提示。检查点: 三桥 stdio 握手、8765 health、
routing_loaded、路由派生文件新鲜度 (mtime vs bridge 表)、插件版本、DB 存在性。

## 四、关键机制 (防再踩)

1. **双 venv 边界**: hermes 本体 venv 已 pin `mcp==2.0.0` (无 fastmcp);
   三桥专用 `mcp1x-venv` (mcp==1.28.1)。任何一方升级, 另一方不受影响。
   新桥一律进 mcp1x-venv。
2. **注册走 CLI**: `hermes mcp add <name> --command <venv python> --args <script>`;
   交互提示 "Enable all N tools?" 用 `yes y |` 管道喂。config 禁直改。
3. **注册态≠运行态**: `hermes mcp list` 显示 enabled 只代表配置存在。
   判活必须 stdio 握手 (initialize→tools/list) 或看会话工具目录。
4. **路由表是派生物**: 冻结源 = `bridge/topology_routing_table.yaml` (I1-I6);
   sidecar 消费格式 = 顶层 `routes:` + query_axes 拼接 key。
   改冻结源后: `python3 /mnt/d/hermes_memory/maintenance/gen_sidecar_routes.py`
   → 重启 sidecar。
5. **插件更新流程**: sanyuan 仓 integration/obsidian 分支 → worktree 取源 →
   `npm ci && npm run build` → 拷 main.js/styles.css/manifest.json 到
   `/mnt/d/GEO/.obsidian/plugins/sanyuan-context-router/` → bump manifest version
   → Obsidian 内重载。旧版先备份。
6. **query_axes 用法**: 笔记 frontmatter 写 `sanyuan_axes: 域, 条目名`
   (逗号分隔), 插件检索时自动带上该条目的跨域投影 (routing 字段)。

## 五、事故 Runbook

### R1 | MCP 桥全死 (hermes 升级后)
症状: 工具目录无 vault_*; 手动跑桥报 `No module named 'mcp.server.fastmcp'`。
根因: hermes 本体 venv 的 mcp 大版本变更, 三桥曾共居该 venv 被连坐 (08-18/19 实际发生)。
修复: 确认桥在 mcp1x-venv (§四.1); 不在则 `yes y | hermes mcp add ...` 迁移;
握手验证; 新会话生效。

### R2 | sidecar 不通
症状: curl 127.0.0.1:8765/health 无响应。
修复: `bash ~/.hermes/mcp_servers/start_sanyuan_sidecar.sh` 后台拉起 → health。
注意: 服务属长驻进程, 用 Hermes 的 background=true 拉起, 禁 nohup。

### R3 | routing_loaded: false
症状: health 返回 routing_loaded=False。
诊断链: degradation=routing-table-missing → 路径错;
=has-no-routes → 喂了冻结源而非派生文件; =yaml-parser-unavailable → 缺 pyyaml。
修复: 确认 SANYUAN_ROUTING_TABLE 指向 sidecar_routes.yaml; 过期则重跑生成器。

### R4 | 插件旧/破图
症状: 插件功能缺失 (无 browse-sanyuan-nodes 等)。
修复: 按 §四.5 从 integration/obsidian 分支重建。

### R5 | L5 context.json 死链 (已知未修)
症状: context=null, updatedAt 停在旧日期 (08-03)。
性质: 插件侧停止写入, 与 MCP/sidecar 无关。修复需查 Obsidian hermes-console
插件状态。**未修, 待案**。

## 六、边界

- 本模块不管认知流程 (归 consciousness-bus) 和归一化数据面 (归 sanyuan-normalization-port)
- 冻结资产 (bridge 表 / 三才定义) 只读; 一切适配通过派生文件
- 三桥源码目前仍是本地孤儿 (无版本控制) — 收编进仓是待办, 收编前本 skill 的
  scripts/router_health.py 是唯一的链路巡检入口

## 七、自测清单

- [ ] router_health.py 全绿 → 链路可用
- [ ] 三桥握手各自返回 6/2/5 工具
- [ ] health: status=ok 且 routing_loaded=True
- [ ] POST /v1/retrieve-and-inject 带 query_axes 能返回 routing 字段
- [ ] hermes 本体 venv 升级后重跑 router_health.py 能立刻暴露断桥

> 版本: 0.1.0 | 2026-08-25 | 来源: 2026-08-25 全链路修复战役 (见 source/)
