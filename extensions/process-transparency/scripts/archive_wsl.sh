#!/bin/bash
# archive_wsl.sh — WSL侧记忆归档 → 压缩 → D盘 (两阶段工作流)
# 设计意图 (用户, 2026-08-07):
#   归档指令发出前: 记忆备份在WSL内 (活跃区, 可回滚)
#   归档指令发出后: WSL内记忆 → 压缩 → 扔到Windows D盘
# 纪律: 耻辱柱 — 跨/mnt桥禁止rsync大目录复制, 用tar原地压缩再移
#
# 用法:
#   archive_wsl.sh now     — 立即归档当前WSL侧记忆
#   archive_wsl.sh status  — 显示WSL/D盘两侧记忆状态

set -e
WSL_MEM="$HOME/.hermes/memories"
ARCHIVE_DIR="/mnt/d/hermes_memory/archive/记忆快照"
LOG="/mnt/d/hermes_memory/maintenance/sync.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

# ── 归档: WSL压缩 → D盘 ──
do_archive() {
    local stamp=$(date '+%Y%m%d_%H%M%S')
    mkdir -p "$ARCHIVE_DIR"

    log "ARCHIVE: WSL侧记忆 → 压缩 → D盘"
    log "  来源: $WSL_MEM ($(du -sh "$WSL_MEM" 2>/dev/null | cut -f1))"

    # 1. 先在WSL侧原地压缩 (耻辱柱: 禁跨桥复制)
    local tarball="/tmp/hermes_memory_wsl_${stamp}.tar.gz"
    tar -czf "$tarball" -C "$HOME/.hermes" memories 2>/dev/null

    # 2. 压缩包移动到D盘 (单文件移动, 非大目录复制)
    mv "$tarball" "$ARCHIVE_DIR/"
    local final="$ARCHIVE_DIR/hermes_memory_wsl_${stamp}.tar.gz"

    log "  压缩包: $final ($(du -sh "$final" | cut -f1))"
    log "  ARCHIVE 完成 — WSL侧记忆已压缩扔到D盘"
    echo "ARCHIVED: $final"
}

# ── 状态 ──
show_status() {
    echo "=== WSL侧 (活跃区) ==="
    du -sh "$WSL_MEM" 2>/dev/null || echo "无"
    wc -l "$WSL_MEM/MEMORY.md" 2>/dev/null
    echo ""
    echo "=== D盘 (归档区) ==="
    ls -la "$ARCHIVE_DIR/" 2>/dev/null | tail -5 || echo "无归档"
    echo ""
    echo "=== 最近归档 ==="
    ls -t "$ARCHIVE_DIR/"*.tar.gz 2>/dev/null | head -3 || echo "从未归档"
}

case "${1:-status}" in
    now)   do_archive ;;
    status|*) show_status ;;
esac
