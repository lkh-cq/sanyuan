"""Boundary Task (B_T) 与 hive 身份 (M1 骨架, 合同见 schemas/)."""

import hashlib
import json
from pathlib import Path

SCHEMAS = Path(__file__).resolve().parent.parent.parent / "schemas"


def boundary_hash(boundary: dict) -> str:
    """对 B_T 的 canonical JSON 计算 sha256。generation 内不可变。"""
    payload = json.dumps(
        {k: boundary[k] for k in ("task_goal", "source_scope", "stop_condition", "forbidden_loss")},
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def assert_hive_scope(record: dict, expected_hive_id: str, expected_hash: str) -> None:
    """hive_id / boundary_hash 不匹配必须 fail-closed。"""
    if record.get("hive_id") != expected_hive_id:
        raise ValueError("hive_id mismatch: fail-closed")
    if record.get("boundary_hash") != expected_hash:
        raise ValueError("boundary_hash mismatch: fail-closed")
