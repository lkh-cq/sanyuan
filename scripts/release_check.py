"""发布前检查: 版本源 + 工作区状态 + 提交哈希 + tag 闭环。

防止把未提交的本地实现误判为已发布 (Fullstack 0.4.0a2 教训):
- 版本只从 pyproject.toml 读取, 并与 src/sanyuan_hive/__init__.py 比对;
- 工作区必须干净 (无未提交修改/新增);
- 输出当前 commit 与 hive-v<version> tag 是否存在;
- 任一不一致返回非零退出码。

用法: python3 scripts/release_check.py
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
INIT = ROOT / "src" / "sanyuan_hive" / "__init__.py"

_VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
_INIT_VERSION_RE = re.compile(r'^__version__\s*=\s*"([^"]+)"', re.MULTILINE)


def _git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return proc.stdout.strip()


def main() -> int:
    errors: list[str] = []

    # 1. 版本源: pyproject.toml
    pyproject_text = PYPROJECT.read_text(encoding="utf-8")
    m = _VERSION_RE.search(pyproject_text)
    if not m:
        errors.append("pyproject.toml: version not found")
        return 1
    version = m.group(1)

    # 2. 与 __init__.py 比对
    init_text = INIT.read_text(encoding="utf-8")
    im = _INIT_VERSION_RE.search(init_text)
    if not im:
        errors.append(f"{INIT}: __version__ not found")
    elif im.group(1) != version:
        errors.append(
            f"version mismatch: pyproject={version} vs __init__={im.group(1)}"
        )

    # 3. 工作区状态
    status = _git(["status", "--porcelain"])
    if status:
        errors.append(f"working tree not clean:\n{status}")

    # 4. 提交哈希与 tag 闭环
    head = _git(["rev-parse", "HEAD"])
    tag = f"hive-v{version}"
    tags = _git(["tag", "--list", tag]).splitlines()
    tag_exists = tag in tags

    print(f"version={version}")
    print(f"commit={head}")
    print(f"tag={tag}")
    print(f"tag_exists={tag_exists}")
    print(f"working_tree_clean={not status}")
    print(
        f"version_sources_consistent={not any('version mismatch' in e for e in errors)}"
    )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
