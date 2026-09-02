"""hive CLI 入口 (M1 骨架)."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="hive", description="sanyuan-hive CLI (M1 skeleton)"
    )
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if args.version:
        from sanyuan_hive import __version__

        print(__version__)
