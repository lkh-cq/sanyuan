# 2026-08-25 全链路修复战役 — 溯源记录 (provenance)

## 事故链

1. **08-18/19**: hermes-agent 升级, pyproject.toml pin `mcp==2.0.0`
   (starlette CVE-2026-48710 修复连带)。mcp 2.0 删除 `mcp.server.fastmcp` 入口。
2. **静默期 08-19 → 08-25**: obsidian-memory / playwright_bridge / shellbox
   三桥 import 即死。`hermes mcp list` 仍显示 enabled (配置态≠运行态),
   无任何告警。DB 最后写入 08-15 08:20 是死亡时间窗证据。
3. **08-25 发现**: 用户报"插件很久没更新"→ 排查 → 根因定位 → 全链路修复。

## 修复动作 (全部有磁盘证据)

| # | 动作 | 证据 |
|---|------|------|
| 1 | 建隔离 venv `~/.hermes/mcp_servers/mcp1x-venv` 装 mcp==1.28.1 | import 过闸输出 |
| 2 | 三桥逐个 stdio 握手 (6/5/2 工具) | tools/list 响应 |
| 3 | `yes y \| hermes mcp add` 重注册三桥 | config.yaml 路径变更 |
| 4 | vault 写探针→读回→写后即时检索→清理 | FTS 命中输出 |
| 5 | 拉起 8765 sidecar | health status=ok |
| 6 | 发现 routing_loaded=false → 读 topology.py 源码定位 schema 错配 | `routes:` 键 + query_axes key 拼接 |
| 7 | 写 `maintenance/gen_sidecar_routes.py` 派生器 (冻结 bridge 表→52 routes) | 派生文件+样例验证 |
| 8 | 启动脚本接 `SANYUAN_ROUTING_TABLE` 环境变量 | patch diff |
| 9 | 带轴查询命中 I3 本体+4 跨域投影 | POST 响应 routing 字段 |
| 10 | 插件 0.1.1→0.2.0 (worktree 构建 integration/obsidian 分支 b930c8d) | main.js 含 browse-sanyuan-nodes, 旧版备份 .bak-20260825 |
| 11 | playwright==1.62.0 装入隔离 venv; shellbox/playwright 真值实测 (WSL 命令执行 + example.com 导航 HTTP 200) | 实测输出 |

## 关键设计判断

- **冻结资产不改**: bridge/topology_routing_table.yaml (I1-I6) 是冻结源;
  sidecar 格式适配走派生文件 (sidecar_routes.yaml), 与藏归"母信息不删除"
  原则同构。
- **薄适配层先例**: 仓内 workflow/continuous 的 mcp/server.py 已确立
  "stdlib 核心 + 可丢弃适配层"模式; 三桥下一步治理方向 = 拆分收编 (未做)。
- **判断教训**: ①tool_search 搜不到 ≠ 未挂载 (注册层/会话加载层是两层);
  ②只看本地残骸不开云端图纸 (云端 workflow/continuous 早有正确形态);
  ③`mcp list` enabled ≠ 进程存活。

## 遗留

- 三桥源码收编进仓 (消除孤儿状态) — 待办
- L5 context.json 死链 (08-03 起) — 待案
- 云端 experiment/multiscale-reinjection-kernel 分支 29 commits 未合并 — 用户决策
