#!/usr/bin/env python3
"""sanyuan-harness MCP adapter (stdio)。

向 agent 暴露四个工具，全部委托给仓库内 stdlib-only 的既有脚本，本文件只是薄适配层：
  sanyuan.mode_status   -> 读取 reference/flow/active-state.json
  sanyuan.set_mode      -> 经 scripts/harness_state.py set 写入模式
  sanyuan.run_pipeline  -> scripts/endoscope.py pipeline（只读）
  sanyuan.probe_source  -> scripts/endoscope.py probe（只读）

唯一新增非标准库依赖：官方 `mcp` 包（仅限本适配器）。核心协议逻辑仍在零依赖脚本中。
MCP 为多 agent 通用协议（Claude Code / Codex / Gemini CLI 等均支持）。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[3]
HARNESS = ROOT / "scripts" / "harness_state.py"
ENDOSCOPE = ROOT / "scripts" / "endoscope.py"
STATE_PATH = ROOT / "reference" / "flow" / "active-state.json"

mcp = FastMCP("sanyuan-harness")

VALID_MODES = ("armed", "deep", "direct")


def _run(cmd: list[str], timeout: int = 90) -> dict:
    proc = subprocess.run(
        cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout
    )
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _run_json(cmd: list[str], timeout: int = 90) -> dict:
    result = _run(cmd, timeout)
    parsed = None
    if result["stdout"]:
        try:
            parsed = json.loads(result["stdout"])
        except json.JSONDecodeError:
            pass
    result["parsed"] = parsed
    return result


@mcp.tool()
def mode_status() -> dict:
    """返回当前 harness 工作流模式与状态文件内容。"""
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        state = {"mode": "armed", "task_profile": None, "last_gate": None}
    return {"mode": state.get("mode"), "state": state, "state_path": str(STATE_PATH)}


@mcp.tool()
def set_mode(
    mode: str,
    task_profile: str | None = None,
    last_gate: dict | None = None,
) -> dict:
    """进入/退出深度模式。mode ∈ {armed, deep, direct}；可选记录 task_profile 与 last_gate。"""
    if mode not in VALID_MODES:
        return {"ok": False, "error": f"invalid mode {mode!r}; expected armed|deep|direct"}
    cmd = [sys.executable, str(HARNESS), "set", "--mode", mode]
    if task_profile:
        cmd += ["--task-profile", task_profile]
    if last_gate is not None:
        cmd += ["--last-gate", json.dumps(last_gate)]
    return _run(cmd)


@mcp.tool()
def probe_source(path: str) -> dict:
    """对单个源文件运行 Endoscope 只读探针（不修改文件）。"""
    target = Path(path).resolve()
    if not target.is_file():
        return {"ok": False, "error": f"file not found: {path}"}
    return _run_json([sys.executable, str(ENDOSCOPE), "probe", str(target)])


@mcp.tool()
def run_pipeline(
    task_family: str,
    source: str | None = None,
    snapshot: str | None = None,
    event: dict | None = None,
    scope: int | None = None,
    blast: int | None = None,
    uncertainty: int | None = None,
    dependency: int | None = None,
    tainted: bool = False,
    irreversible: bool = False,
) -> dict:
    """运行完整 TaskProfile→probe→NSL→revival→E/S/O 管线（只读）。task_family 见 endoscope-task-profiles.json。"""
    cmd = [sys.executable, str(ENDOSCOPE), "pipeline", "--task-family", task_family]
    if source:
        cmd += ["--source", str(Path(source).resolve())]
    if snapshot:
        cmd += ["--snapshot", str(Path(snapshot).resolve())]
    if event is not None:
        cmd += ["--event-json", json.dumps(event)]
    for name, value in (
        ("scope", scope),
        ("blast", blast),
        ("uncertainty", uncertainty),
        ("dependency", dependency),
    ):
        if value is not None:
            cmd += [f"--{name}", str(value)]
    if tainted:
        cmd.append("--tainted")
    if irreversible:
        cmd.append("--irreversible")
    return _run_json(cmd)


def main() -> int:
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
