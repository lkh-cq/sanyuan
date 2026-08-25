#!/usr/bin/env python3
"""sanyuan-router 链路健康检查 — 一条命令巡检全部九条线路。

用法: python3 router_health.py
退出码: 0=全绿, 1=有FAIL。每条线路给 PASS/FAIL/SKIP + 修复提示。
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

HOME = Path.home()
VENV_PY = HOME / ".hermes/mcp_servers/mcp1x-venv/bin/python"
MCP_DIR = HOME / ".hermes/mcp_servers"
BRIDGE_TABLE = Path("/mnt/d/hermes_memory/bridge/topology_routing_table.yaml")
ROUTES = Path("/mnt/d/hermes_memory/bridge/sidecar_routes.yaml")
DB = Path("/mnt/d/hermes_memory/maintenance/obsidian-memory.db")
PLUGIN_DIR = Path("/mnt/d/GEO/.obsidian/plugins/sanyuan-context-router")
SIDECAR_START = MCP_DIR / "start_sanyuan_sidecar.sh"

BRIDGES = [
    ("L1 obsidian-memory", MCP_DIR / "obsidian-memory.py", 6),
    ("L2 playwright-bridge", MCP_DIR / "playwright_bridge.py", 5),
    ("L3 shellbox", MCP_DIR / "shellbox.py", 2),
]

results: list[tuple[str, str, str]] = []  # (line, status, note)


def add(line: str, ok: bool, note: str, skip: bool = False) -> None:
    status = "SKIP" if skip else ("PASS" if ok else "FAIL")
    results.append((line, status, note))


def stdio_tools(script: Path) -> tuple[int | None, str]:
    """对 stdio MCP 桥做 initialize→tools/list 握手, 返回 (工具数, 错误信息)。"""
    if not script.exists():
        return None, f"脚本不存在: {script}"
    if not VENV_PY.exists():
        return None, f"隔离 venv 缺失: {VENV_PY}"
    payload = (
        '{"jsonrpc":"2.0","id":1,"method":"initialize","params":'
        '{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"health","version":"0"}}}\n'
        '{"jsonrpc":"2.0","method":"notifications/initialized"}\n'
        '{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n'
    )
    try:
        proc = subprocess.run(
            [str(VENV_PY), str(script)],
            input=payload, capture_output=True, text=True, timeout=20,
        )
    except subprocess.TimeoutExpired:
        return None, "握手超时 (>20s)"
    for line in proc.stdout.splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("id") == 2:
            return len(d["result"]["tools"]), ""
    return None, f"无 tools/list 响应 (stderr: {proc.stderr.strip()[:80]})"


def main() -> int:
    # L1-L3: 三桥握手
    for name, script, expect in BRIDGES:
        n, err = stdio_tools(script)
        if n is None:
            add(name, False, f"{err} → 修复: 见 sanyuan-router skill R1")
        elif n != expect:
            add(name, False, f"工具数 {n} ≠ 预期 {expect}")
        else:
            add(name, True, f"{n}/{expect} 工具握手正常")

    # 注册态核对 (config 指向)
    cfg = HOME / ".hermes/config.yaml"
    if cfg.exists():
        text = cfg.read_text(encoding="utf-8")
        # 逐桥查 config 段内是否还有旧 venv 路径
        for name, script, _ in BRIDGES:
            short = name.split()[1]
            seg = text.split(f"{short}:", 1)
            if len(seg) > 1:
                block = seg[1].split("\n\n", 1)[0][:400]
                if "hermes-agent/venv" in block:
                    add(name + "/注册", False, "config 仍指旧 venv → R1")
                else:
                    add(name + "/注册", True, "指向隔离 venv")
            else:
                add(name + "/注册", False, "config 无此桥注册段")

    # L4: sidecar
    try:
        with urllib.request.urlopen("http://127.0.0.1:8765/health", timeout=5) as r:
            h = json.loads(r.read())
        add("L4 sidecar/health", h.get("status") == "ok",
            f"status={h.get('status')}")
        rl, rd = h.get("routing_loaded"), h.get("routing_degradation")
        add("L4 sidecar/routing", bool(rl),
            f"loaded={rl} degradation={rd}" + ("" if rl else " → R3"))
    except Exception as e:  # noqa: BLE001
        add("L4 sidecar/health", False, f"8765 不通 ({e}) → 修复: bash {SIDECAR_START}")

    # 路由派生文件新鲜度
    if BRIDGE_TABLE.exists() and ROUTES.exists():
        stale = ROUTES.stat().st_mtime < BRIDGE_TABLE.stat().st_mtime
        add("L4 路由派生新鲜度", not stale,
            "sidecar_routes.yaml 落后于冻结 bridge 表 → 重跑 gen_sidecar_routes.py"
            if stale else f"{len(ROUTES.read_text())}B, 晚于 bridge 表")
    elif not ROUTES.exists():
        add("L4 路由派生新鲜度", False, "sidecar_routes.yaml 不存在 → 重跑生成器")
    else:
        add("L4 路由派生新鲜度", False, "冻结 bridge 表缺失")

    # DB
    add("vault DB", DB.exists(), f"{DB}" + ("" if DB.exists() else " → 检查 vault 路径"))

    # 插件
    mf = PLUGIN_DIR / "manifest.json"
    if mf.exists():
        try:
            ver = json.loads(mf.read_text(encoding="utf-8")).get("version", "?")
            has_new = "browse-sanyuan-nodes" in (PLUGIN_DIR / "main.js").read_text(encoding="utf-8")
            add("L-插件 sanyuan-context-router", has_new,
                f"v{ver}, 新功能{'在' if has_new else '缺失 → R4 (需从分支重建)'}")
        except Exception as e:  # noqa: BLE001
            add("L-插件 sanyuan-context-router", False, str(e))
    else:
        add("L-插件 sanyuan-context-router", False, f"{PLUGIN_DIR} 不存在")

    # L5-L9 存在性 (弱检查)
    for name, path in [
        ("L5 context.json", Path("/mnt/d/GEO/.obsidian/hermes/context.json")),
        ("L6 mirror bus", HOME / ".hermes/mirror/bus.jsonl"),
        ("L7 soul_echo", HOME / ".hermes/mirror/soul_echo.jsonl"),
        ("L9 冻结 bridge 表", BRIDGE_TABLE),
    ]:
        add(name + "(存在性)", path.exists(), str(path))

    # 汇总
    print("=" * 64)
    print("sanyuan-router 链路健康检查")
    print("=" * 64)
    fails = 0
    for line, status, note in results:
        mark = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭"}[status]
        if status == "FAIL":
            fails += 1
        print(f"{mark} {status:<4} {line:<28} {note[:60]}")
    print("=" * 64)
    print(f"结果: {len(results) - fails}/{len(results)} PASS, {fails} FAIL")
    if fails:
        print("修复手册: skill_view(name='sanyuan-router') §五 Runbook")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
