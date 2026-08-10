from __future__ import annotations

import argparse
import json
import os
from dataclasses import replace
from pathlib import Path

from .config import PipelineConfig
from .pipeline import ContextPipeline
from .server import serve


def _pipeline(database: str | None) -> ContextPipeline:
    config = PipelineConfig.from_env()
    if database:
        config = replace(config, database_path=Path(database).expanduser())
    return ContextPipeline(config)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sanyuan-obsidian",
        description="Obsidian retrieval and Sanyuan read-injection sidecar",
    )
    parser.add_argument("--db", help="path to obsidian-memory SQLite database")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inspect", help="inspect database capabilities")

    query = subparsers.add_parser("query", help="run one retrieval request")
    query.add_argument("text")
    query.add_argument("--top-k", type=int, default=8)
    query.add_argument("--mode", choices=("full", "fast", "minimal"), default="full")
    query.add_argument(
        "--trigger-policy", choices=("always", "auto", "never"), default="always"
    )
    query.add_argument("--axis", action="append", dest="axes")
    query.add_argument("--json", action="store_true", dest="as_json")

    server = subparsers.add_parser("serve", help="start loopback REST sidecar")
    server.add_argument("--host", default="127.0.0.1")
    server.add_argument("--port", type=int, default=8765)
    server.add_argument("--allow-remote", action="store_true")

    reindex = subparsers.add_parser(
        "reindex", help="build the sidecar-owned vector index from the detected FTS table"
    )
    reindex.add_argument("--limit", type=int)
    reindex.add_argument("--batch-size", type=int, default=16)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    pipeline = _pipeline(args.db)
    if args.command == "inspect":
        print(json.dumps(pipeline.health(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "query":
        result = pipeline.retrieve_and_inject(
            args.text,
            top_k=args.top_k,
            mode=args.mode,
            trigger_policy=args.trigger_policy,
            query_axes=args.axes,
        )
        print(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
            if args.as_json
            else result.injection
        )
        return 0
    if args.command == "serve":
        loopback = {"127.0.0.1", "::1", "localhost"}
        if args.host not in loopback and not args.allow_remote:
            raise SystemExit("non-loopback bind requires --allow-remote")
        token = os.environ.get("SANYUAN_SIDECAR_TOKEN")
        serve(pipeline, host=args.host, port=args.port, token=token)
        return 0
    if args.command == "reindex":
        if not pipeline.embedder.enabled:
            raise SystemExit("embedding configuration is required for reindex")
        candidates = list(pipeline.store.iter_fts(limit=args.limit))
        batch_size = max(1, min(64, args.batch_size))
        indexed = 0
        for offset in range(0, len(candidates), batch_size):
            batch = candidates[offset : offset + batch_size]
            vectors = pipeline.embedder.embed(
                [candidate.content[:6000] for candidate in batch]
            )
            for candidate, vector in zip(batch, vectors):
                pipeline.store.upsert_vector(candidate, vector)
                indexed += 1
        print(json.dumps({"indexed": indexed}, ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
