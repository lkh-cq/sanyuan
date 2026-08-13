#!/usr/bin/env bash
# Sanyuan Obsidian sidecar 一键启动
# sidecar 源码: integrations/obsidian/python/（同仓库）
# 呼出"意识总线/sanyuan"时,若 8765 无监听则执行本脚本自动拉起。
set -euo pipefail

SIDECAR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../python" && pwd)"
DB_PATH="${SANYUAN_OBSIDIAN_DB:-/mnt/d/hermes_memory/maintenance/obsidian-memory.db}"

cd "$SIDECAR_DIR"
exec env PYTHONPATH=src python3 -m sanyuan_obsidian --db "$DB_PATH" serve --host 127.0.0.1 --port 8765
