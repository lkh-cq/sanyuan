#!/usr/bin/env python3
"""Harness 持续工作流状态机（stdlib-only，跨 agent 通用）。

维护 reference/flow/active-state.json 中的工作流模式状态：
  armed   — 就绪，未确认深度；首个实质任务应先询问用户
  deep    — 深度模式已激活，执行完整 B_T→TaskProfile→归一化→NSL→闸门
  direct  — 直接模式，保持轻量，不展开总线

命令：
  start    初始化/重置为 armed，打印就绪行
  inject   打印当前模式一行
  set      设置 --mode deep|direct|armed，可选 --task-profile / --last-gate
  snapshot 确保状态已落盘
  persist  最终持久化
  show     打印完整状态 JSON（调试 / MCP 用）

任意 agent（Claude Code / Codex / Gemini CLI / Hermes 等）均可调用。
需要每轮自动注入一行时，可在各自 harness 配置中把 `inject` 挂到每轮开始
（例如 Claude Code 的 UserPromptSubmit hook）。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "reference" / "flow" / "active-state.json"

VALID_MODES = ("armed", "deep", "direct")

_MODE_LINES = {
    "armed": (
        "sanyuan 工作流已就绪（armed）：尚未进入深度模式，不要展开完整管线；"
        "首个实质任务应先询问用户是否进入深度模式。"
    ),
    "deep": (
        "sanyuan 深度模式已激活：按 B_T→TaskProfile→归一化→NSL→闸门执行，遵守 AGENTS.md 硬规则。"
    ),
    "direct": "sanyuan 直接模式：保持轻量，不展开总线。",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_state() -> dict:
    return {
        "protocol": "harness-continuous",
        "mode": "armed",
        "task_profile": None,
        "last_gate": None,
        "updated_at": _now(),
    }


def _load() -> dict:
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    return _default_state()


def _save(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _mode_line(state: dict) -> str:
    mode = state.get("mode", "armed")
    if mode not in _MODE_LINES:
        mode = "armed"
    line = _MODE_LINES[mode]
    extra: list[str] = []
    if state.get("task_profile"):
        extra.append(f"TaskProfile={state['task_profile']}")
    gate = state.get("last_gate")
    if isinstance(gate, dict) and gate.get("execution"):
        extra.append(
            f"上轮闸门={gate.get('execution')}/{gate.get('state')}/{gate.get('output')}"
        )
    if extra:
        line += " | " + " | ".join(extra)
    return line


def _cmd_start() -> int:
    _save(_default_state())
    print("sanyuan-harness: ready (armed)")
    print(_mode_line(_default_state()))
    return 0


def _cmd_inject() -> int:
    print(_mode_line(_load()))
    return 0


def _cmd_set(mode: str, task_profile: str | None, last_gate: str | None) -> int:
    if mode not in VALID_MODES:
        print(
            f"sanyuan-harness: invalid mode {mode!r}; expected {', '.join(VALID_MODES)}",
            file=sys.stderr,
        )
        return 2
    state = _load()
    state["mode"] = mode
    if task_profile is not None:
        state["task_profile"] = task_profile or None
    if last_gate is not None:
        try:
            parsed = json.loads(last_gate)
        except json.JSONDecodeError:
            print("sanyuan-harness: --last-gate must be a JSON object", file=sys.stderr)
            return 2
        state["last_gate"] = parsed if isinstance(parsed, dict) else None
    state["updated_at"] = _now()
    _save(state)
    print(f"sanyuan-harness: mode -> {mode}")
    return 0


def _cmd_snapshot() -> int:
    _save(_load())
    print("sanyuan-harness: snapshot ok")
    return 0


def _cmd_persist() -> int:
    _save(_load())
    print("sanyuan-harness: persisted")
    return 0


def _cmd_show() -> int:
    print(json.dumps(_load(), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="harness_state")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("start")
    sub.add_parser("inject")
    set_parser = sub.add_parser("set")
    set_parser.add_argument("--mode", required=True, choices=VALID_MODES)
    set_parser.add_argument("--task-profile")
    set_parser.add_argument("--last-gate")
    sub.add_parser("snapshot")
    sub.add_parser("persist")
    sub.add_parser("show")
    args = parser.parse_args()

    if args.command == "start":
        return _cmd_start()
    if args.command == "inject":
        return _cmd_inject()
    if args.command == "set":
        return _cmd_set(args.mode, args.task_profile, args.last_gate)
    if args.command == "snapshot":
        return _cmd_snapshot()
    if args.command == "persist":
        return _cmd_persist()
    if args.command == "show":
        return _cmd_show()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
