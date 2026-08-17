"""Boundary Task (B_T) 与 hive 身份 (M1 骨架, 合同随包分发)."""

import hashlib
import json
from importlib import resources

HASH_FIELDS = ("task_goal", "source_scope", "stop_condition", "forbidden_loss")


def _schemas_dir():
    """优先读 wheel 内打包的 schemas, 回退 repo 相对路径。"""
    try:
        with resources.as_file(resources.files("sanyuan_hive") / "schemas") as p:
            return p
    except Exception:
        from pathlib import Path

        return Path(__file__).resolve().parent.parent.parent / "schemas"


def boundary_hash(boundary: dict) -> str:
    """对 B_T 的 canonical JSON 计算 sha256。generation 内不可变。

    哈希字段固定为 HASH_FIELDS 四元组, 不含 created_at/status。
    """
    payload = json.dumps(
        {k: boundary[k] for k in HASH_FIELDS},
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
