#!/usr/bin/env bash
# 批量 Endoscope 只读审计（跨 agent 通用）。
#
# 用法: bash scripts/harness_audit.sh <file...>
# 对每个文件运行 scripts/endoscope.py probe（只读，不修改任何源文件），
# 按闸门严重度排序输出 JSON 报告。纯依赖: bash + python3（stdlib）。
#
# 输出字段:
#   audited / requested / not_probed
#   by_severity: irreversible_write / high_or_critical / clean 三类路径分组
#   ranked: 按严重度降序排列的逐文件结果
#     severity: 4=irreversible_write, 3=high_or_critical>=2, 2=high_or_critical>=1,
#               1=signal_count>=1, 0=clean

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENDOSCOPE="$ROOT/scripts/endoscope.py"

if [ "$#" -eq 0 ]; then
  echo "用法: bash scripts/harness_audit.sh <file...>" >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "harness_audit: 需要 python3" >&2
  exit 1
fi

export HARNESS_AUDIT_ENDOSCOPE="$ENDOSCOPE"
python3 - "$@" <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path

endoscope = Path(os.environ["HARNESS_AUDIT_ENDOSCOPE"])
results = []
for raw in sys.argv[1:]:
    path = str(raw)
    target = Path(raw)
    if not target.is_file():
        results.append({
            "path": path, "exit_code": -1, "probe_error": "file not found",
            "language": None, "parse_ok": None, "signal_count": 0,
            "high_or_critical": 0, "irreversible_write": False, "top_signals": [],
        })
        continue
    proc = subprocess.run(
        [sys.executable, str(endoscope), "probe", str(target)],
        text=True, capture_output=True, timeout=90,
    )
    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        data = {}
    if proc.returncode != 0 or data.get("status") == "ERROR":
        results.append({
            "path": path, "exit_code": proc.returncode,
            "probe_error": data.get("error") or proc.stderr.strip() or "probe failed",
            "language": None, "parse_ok": None, "signal_count": 0,
            "high_or_critical": 0, "irreversible_write": False, "top_signals": [],
        })
        continue
    summary = data.get("summary") or {}
    signals = sorted({str(o.get("signal")) for o in data.get("observations", [])
                      if isinstance(o, dict) and o.get("signal")})
    results.append({
        "path": path,
        "exit_code": proc.returncode,
        "probe_error": None,
        "language": (data.get("target") or {}).get("language"),
        "parse_ok": (data.get("syntax") or {}).get("parse_ok"),
        "signal_count": summary.get("signal_count", 0),
        "high_or_critical": summary.get("high_or_critical", 0),
        "irreversible_write": bool(summary.get("irreversible_write")),
        "top_signals": signals,
    })


def severity(r):
    if r["irreversible_write"]:
        return 4
    if r["high_or_critical"] >= 2:
        return 3
    if r["high_or_critical"] >= 1:
        return 2
    if r["signal_count"] >= 1:
        return 1
    return 0


results.sort(key=lambda r: (-severity(r), str(r["path"])))
probed = [r for r in results if r["exit_code"] != -1]
report = {
    "audited": len(probed),
    "requested": len(results),
    "by_severity": {
        "irreversible_write": [r["path"] for r in results if r["irreversible_write"]],
        "high_or_critical": [r["path"] for r in results
                             if not r["irreversible_write"] and r["high_or_critical"] > 0],
        "clean": [r["path"] for r in results
                  if not r["irreversible_write"] and r["high_or_critical"] == 0 and r["exit_code"] != -1],
    },
    "ranked": results,
    "not_probed": [r["path"] for r in results if r["exit_code"] == -1],
}
print(json.dumps(report, ensure_ascii=False, indent=2))
PY
