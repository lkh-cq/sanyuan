# Obsidian 集成（integration/obsidian）

> 状态：本目录在 main 上**不携带可复现源码**。完整实现（Python sidecar、TypeScript 插件源码、测试、检索、rerank 与写回能力）位于 `integration/obsidian` 分支，尚未合并进 main。

## 源码位置

- 分支：`https://github.com/lkh-cq/sanyuan/tree/integration/obsidian`
- 内容：`integrations/obsidian/python`（stdlib-only sidecar）、`integrations/obsidian/plugin`（TypeScript 插件源码 + 构建配置）、测试与检索/rerank/写回能力。

## 为什么 main 上没有构建产物

- 构建产物（`main.js`、`.egg-info/`、`sidecar.env`）是**不可复现**的编译/安装残留，不是源码包。
- 主仓校验器 `scripts/validate_bundle.py` 现在会**拒绝** `.egg-info/`、`sidecar.env` 与无 `src/` 兄弟目录的 `main.js`。
- 在 `integration/obsidian` 合并进 main 之前，本目录只保留本说明，避免把构建残留误当作可复现源码。

## 发布契约（待关闭）

- sidecar 需要独立、带 tag 的发布；客户端固定兼容版本；健康检查按契约版本判断功能（如 `browse-sanyuan-nodes`）。
- 详见 [`references/product-topology.md`](../../references/product-topology.md) 的“依赖与版本契约”一节。
