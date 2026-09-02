"""Markdown 内部链接检查: 校验相对链接目标存在, 防止文档断连。

忽略外部链接 (http/https/mailto)、锚点 (#) 与代码块内的链接。
用法: python3 scripts/check_md_links.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# [text](target) 或 [text][ref] 或 [ref]: target
_INLINE_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_REF_DEF = re.compile(r"^\[[^\]]+\]:\s*(\S+)", re.MULTILINE)

_EXTERNAL = ("http://", "https://", "mailto:", "ftp://")


def _is_external(target: str) -> bool:
    return target.startswith(_EXTERNAL + ("#", "<"))


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    # 去掉代码块, 避免误报
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", "", text)
    for m in _INLINE_LINK.finditer(text):
        target = m.group(1).strip()
        if _is_external(target):
            continue
        # 去掉锚点与查询
        target = target.split("#")[0].split("?")[0]
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"{path}: broken link -> {target}")
    for m in _REF_DEF.finditer(text):
        target = m.group(1).strip()
        if _is_external(target):
            continue
        target = target.split("#")[0].split("?")[0]
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"{path}: broken reference link -> {target}")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        errors.extend(check_file(path))
    if errors:
        print("\n".join(errors))
        return 1
    print("all markdown internal links OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
