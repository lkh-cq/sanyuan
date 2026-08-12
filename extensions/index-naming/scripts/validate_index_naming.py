#!/usr/bin/env python3
"""Validate index-file naming against index 命名规范 v2.0.

规则 (见 extensions/index-naming/SKILL.md):
- 命名层级 = 上游目录文件夹个数 (扫描根目录 = 层级 0)
- 层级 0: 根总 INDEX 保留 `_index.md` (全库唯一总入口)
- 层级 1: main branch index —— 内容语义命名 (如 `memory_index.md`) 或三段式 `index.<date>.<内容>.1`
- 层级 >= 2: 子分支 index 严格三段式 `index.<date>.<内容>.<层级>`
  - `<date>`: YYYYMMDD; `<内容>`: 目录主题短词; `<层级>`: 数字 = 上游目录文件夹个数
- 保留项 (v2.0 明确不参与重命名): `_index.md`(根)、`COLOR_INDEX.md`、`GEO_ROOT_INDEX.md`
- 排除运行时/构建噪声: node_modules/ .git/ dist/ __pycache__/ .Rproj.user/

用法:
    python3 validate_index_naming.py [--dry] <扫描根目录>

- 默认: 只读校验, 输出不合规清单。
- --dry: 预览模式, 额外输出每个不合规文件按 v2.0 计算的建议新名; 脚本本身永不写入/重命名。
- 退出码: 0 = 全部合规; 1 = 存在不合规; 2 = 用法/根目录错误。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

# 任意层级保留项 —— v2.0 明确不参与重命名 (小写比较)
# 根 `_index.md` 仅在层级 0 保留, 在层级 >= 1 须按 v2.0 改造, 故不列入此集合。
RESERVED = {"color_index.md", "geo_root_index.md"}

# 运行时/构建噪声目录 —— 不纳入扫描 (小写比较)
EXCLUDED_DIRS = {"node_modules", ".git", "dist", "__pycache__", ".rproj.user"}

# 三段式: index.<YYYYMMDD>.<内容>.<层级>.md
THREE_PART = re.compile(r"index\.(\d{8})\.(.+?)\.(\d+)\.md$", re.IGNORECASE)

DATE_RE = re.compile(r"^\d{8}$")


def is_index_md(path: Path) -> bool:
    """识别目录索引 Markdown 文件。

    命中: index.md / _index.md / index.<date>.<内容>.<层级>.md /
          *_index.md / _index* (如 _index_v1.0.md)。
    不命中: index-xxx.md / index拓扑xxx.md (含 index 但非索引命名)。
    """
    stem = path.stem.lower()
    return (
        stem == "index"
        or stem == "_index"
        or stem.startswith("index.")
        or stem.startswith("_index")
        or stem.endswith("_index")
    )


def upstream_level(path: Path, root: Path) -> int:
    """层级 = 上游目录文件夹个数 (扫描根目录自身 = 0)。"""
    rel = path.relative_to(root)
    return len(rel.parts) - 1


def clean_content(parent: str) -> str:
    """从父目录名推导三段式 `<内容>`: 去数字前缀、规整全角 &。"""
    content = re.sub(r"^\d+_", "", parent)
    content = content.replace("＆", "&")
    return content or "index"


def suggest_new_name(path: Path, level: int) -> str:
    """按 v2.0 为不合规文件计算建议新名 (不写入)。"""
    stem = path.stem.lower()
    match = THREE_PART.match(path.name)
    today = date.today().strftime("%Y%m%d")
    if match:
        # 三段式但层级/日期不符: 保留内容与日期, 修正层级
        return f"index.{match.group(1)}.{match.group(2)}.{level}.md"
    if stem.endswith("_index") and stem != "_index":
        # 内容语义名出现在层级 >= 2: 转三段式, 内容用父目录
        return f"index.{today}.{clean_content(path.parent.name)}.{level}.md"
    # 裸 _INDEX / INDEX / _index_vX: 转三段式, 内容用父目录
    return f"index.{today}.{clean_content(path.parent.name)}.{level}.md"


def validate_file(path: Path, root: Path) -> tuple[bool, str | None, str | None]:
    """校验单个 index 文件。返回 (是否合规, 原因, 建议新名)。"""
    name_lower = path.name.lower()
    level = upstream_level(path, root)

    # 保留项: 不参与重命名, 一律合规
    #   `_index.md` 仅在根目录 (层级 0) 作为总 INDEX 保留;
    #   COLOR_INDEX / GEO_ROOT_INDEX 任意层级保留。
    if name_lower in RESERVED:
        return True, None, None
    if level == 0 and name_lower == "_index.md":
        return True, None, None

    match = THREE_PART.match(path.name)
    if match:
        declared = int(match.group(3))
        if declared != level:
            return (
                False,
                f"三段式层级 {declared} != 上游文件夹个数 {level}",
                suggest_new_name(path, level),
            )
        return True, None, None

    # 非三段式
    stem = path.stem.lower()
    if level == 0:
        return (
            False,
            "层级 0 根目录只允许总 INDEX `_index.md`",
            suggest_new_name(path, level),
        )
    if level == 1:
        if stem.endswith("_index") and stem != "_index":
            # main branch index 内容语义命名 (如 memory_index.md)
            return True, None, None
        return (
            False,
            "层级 1 main branch 应为内容语义命名或三段式 index.<date>.<内容>.1",
            suggest_new_name(path, level),
        )
    # 层级 >= 2: 子分支必须严格三段式
    return (
        False,
        "层级 >= 2 子分支必须严格三段式 index.<date>.<内容>.<层级>",
        suggest_new_name(path, level),
    )


def scan(root: Path) -> tuple[list[tuple[Path, int, str, str | None]], dict]:
    """递归扫描 root, 返回 (不合规清单, 统计)。"""
    violations: list[tuple[Path, int, str, str | None]] = []
    stats = {"md_scanned": 0, "index_found": 0, "compliant": 0, "violations": 0}
    for dirpath, dirnames, filenames in os.walk(root):
        # 就地过滤噪声目录 (os.walk 修改 dirnames 可剪枝)
        dirnames[:] = sorted(
            d for d in dirnames if d.lower() not in EXCLUDED_DIRS
        )
        for filename in sorted(filenames):
            if not filename.lower().endswith(".md"):
                continue
            stats["md_scanned"] += 1
            path = Path(dirpath) / filename
            if not is_index_md(path):
                continue
            stats["index_found"] += 1
            ok, reason, suggestion = validate_file(path, root)
            if ok:
                stats["compliant"] += 1
            else:
                stats["violations"] += 1
                violations.append((path, upstream_level(path, root), reason, suggestion))
    return violations, stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="校验 index 文件命名符合 index 命名规范 v2.0 (层级=上游文件夹个数、三段式)"
    )
    parser.add_argument("root", help="扫描根目录 (该目录自身 = 层级 0)")
    parser.add_argument(
        "--dry",
        action="store_true",
        help="只读预览: 额外输出建议新名; 脚本永不写入/重命名",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: 扫描根目录不存在: {root}", file=sys.stderr)
        return 2

    print(f"扫描根: {root}")
    if args.dry:
        print("模式: --dry 只读预览 (不写入、不重命名)")

    violations, stats = scan(root)

    print(f"扫描 Markdown 文件: {stats['md_scanned']}")
    print(f"命中 index 文件: {stats['index_found']} (合规 {stats['compliant']} / 不合规 {stats['violations']})")

    if not violations:
        print("PASS: 所有 index 文件命名均符合 v2.0")
        return 0

    print("\n不合规清单:")
    for path, level, reason, suggestion in violations:
        rel = path.relative_to(root)
        print(f"  [{level}] {rel}")
        print(f"    原因: {reason}")
        if args.dry and suggestion:
            print(f"    建议: {suggestion}")
    print(f"\nFAIL: {len(violations)} 个 index 文件不合规")
    return 1


if __name__ == "__main__":
    sys.exit(main())
