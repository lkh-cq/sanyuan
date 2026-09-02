"""Boundary Task (B_T) 与 hive 身份 (M1 骨架, 合同随包分发)."""

import hashlib
import json
import re
from importlib import resources
from urllib.parse import unquote

HASH_FIELDS = ("task_goal", "source_scope", "stop_condition", "forbidden_loss")

# URI scheme: source://, md://, file://, https://, ...
_SCOPE_URI_RE = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.-]*)://(.*)$", re.DOTALL)

# 使 scope 退化为全局检索的通配段。
_GLOBAL_SEGMENTS = {"*", "**"}

# 百分号编码的穿越 / 分隔符 token（大小写不敏感）。
_ENCODED_DOT = re.compile(r"%2e", re.IGNORECASE)
_ENCODED_SEPARATOR = re.compile(r"%2f|%5c", re.IGNORECASE)


def _decode_scope_path(path: str) -> list[str]:
    """把 URI path 拆成解码后的段；拒绝编码穿越。

    编码的路径分隔符（%2f/%5c）或点段（%2e）可绕过朴素字符串检查
    走私额外段或 `..` 穿越，因此直接拒绝。
    """
    if _ENCODED_SEPARATOR.search(path):
        raise ValueError("encoded path separator is not allowed")
    if _ENCODED_DOT.search(path):
        raise ValueError("encoded dot segments are not allowed")
    decoded = unquote(path)
    return [seg for seg in decoded.split("/") if seg not in ("", ".")]


def validate_source_scope(source_scope) -> list[str]:
    """校验 source_scope 条目；返回错误消息列表（空 = 合法）。

    Fail-closed 策略：
    - source_scope 必须是非空字符串列表；
    - 每条必须是 scheme:// URI；
    - 禁止裸 "*" / "**" 条目；
    - 禁止根级通配（source://*、source://**、source://*/...）；
    - 禁止 ".." 路径穿越（字面或百分号编码）；
    - 禁止编码路径分隔符；
    - 至少需要一个具体（非通配）路径段。
    """
    errors = []
    if not isinstance(source_scope, list) or not source_scope:
        return ["source_scope must be a non-empty list"]
    for entry in source_scope:
        if not isinstance(entry, str) or not entry:
            errors.append(f"source_scope entry must be a non-empty string: {entry!r}")
            continue
        m = _SCOPE_URI_RE.match(entry)
        if not m:
            errors.append(f"source_scope entry must be a scheme:// URI: {entry!r}")
            continue
        path = m.group(2)
        try:
            segments = _decode_scope_path(path)
        except ValueError as exc:
            errors.append(f"source_scope entry {entry!r}: {exc}")
            continue
        if not segments:
            errors.append(f"source_scope entry {entry!r}: no concrete path anchor")
            continue
        if segments[0] in _GLOBAL_SEGMENTS:
            errors.append(
                f"source_scope entry {entry!r}: wildcard at scope root is global"
            )
            continue
        if ".." in segments:
            errors.append(
                f"source_scope entry {entry!r}: path traversal '..' is not allowed"
            )
            continue
        if all(seg in _GLOBAL_SEGMENTS for seg in segments):
            errors.append(
                f"source_scope entry {entry!r}: no concrete anchor (all wildcards)"
            )
    return errors


def validate_boundary(boundary: dict) -> list[str]:
    """校验完整 B_T；返回错误消息列表（空 = 合法）。"""
    errors = []
    if not isinstance(boundary, dict):
        return ["boundary must be a dict"]
    for field in ("task_goal", "stop_condition"):
        value = boundary.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{field} must be a non-empty string")
    errors.extend(validate_source_scope(boundary.get("source_scope")))
    return errors


def _schemas_dir():
    """优先读 wheel 内打包的 schemas, 回退 repo 相对路径。"""
    try:
        with resources.as_file(resources.files("sanyuan_hive") / "schemas") as p:
            return p
    except Exception:  # noqa: BLE001 - 有意的 wheel→repo 路径兜底
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
