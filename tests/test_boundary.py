"""P0 合同测试: boundary_hash 确定性 + hive scope fail-closed (§12.1)."""

import pytest

from sanyuan_hive.boundary import (
    assert_hive_scope,
    boundary_hash,
    validate_boundary,
    validate_source_scope,
)

BASE_BOUNDARY = {
    "task_goal": "verify one goal",
    "source_scope": ["source://project-a/**"],
    "stop_condition": "F_T passes",
    "forbidden_loss": [],
}


def test_boundary_hash_deterministic():
    assert boundary_hash(BASE_BOUNDARY) == boundary_hash(BASE_BOUNDARY)


def test_boundary_hash_sensitive_to_goal():
    changed = dict(BASE_BOUNDARY, task_goal="different goal")
    assert boundary_hash(changed) != boundary_hash(BASE_BOUNDARY)


def test_missing_hive_id_rejected():
    record = {"boundary_hash": "sha256:" + "0" * 64}
    try:
        assert_hive_scope(record, "hive_20260816_000001", "sha256:" + "0" * 64)
    except ValueError:
        return
    raise AssertionError("missing hive_id must fail-closed")


def test_boundary_hash_mismatch_rejected():
    record = {"hive_id": "hive_20260816_000001", "boundary_hash": "sha256:" + "a" * 64}
    try:
        assert_hive_scope(record, "hive_20260816_000001", "sha256:" + "b" * 64)
    except ValueError:
        return
    raise AssertionError("boundary_hash mismatch must fail-closed")


def test_scope_match_passes():
    h = boundary_hash(BASE_BOUNDARY)
    record = {"hive_id": "hive_20260816_000001", "boundary_hash": h}
    assert_hive_scope(record, "hive_20260816_000001", h)


# --- source_scope 校验 (P0: 等价全局通配 / 路径穿越 / URI 规范化) ---

# 审计列出的等价全局 / 过宽模式与穿越形式, 必须全部拒绝。
INVALID_SCOPES = [
    "*",
    "**",
    "source://*",
    "source://**",
    "source://*/**",
    "md://*",
    "md:///**",
    "source://../etc",
    "source://project/../../etc",
    "source://project/..%2f..%2fetc",
    "source://project/..%2F..%2Fetc",
    "source://%2e%2e/etc",
    "source://%2E%2E/etc",
    "source://",
    "source:///",
    "not-a-uri",
    "",
]


@pytest.mark.parametrize("entry", INVALID_SCOPES)
def test_source_scope_rejects_global_or_traversal(entry):
    assert validate_source_scope([entry]), f"must reject {entry!r}"


# 具体锚定的作用域模式必须接受。
VALID_SCOPES = [
    "source://project-a/**",
    "source://project-a/docs/*.md",
    "md:///project/**",
    "source://project-a",
    "https://example.org/papers/**",
]


@pytest.mark.parametrize("entry", VALID_SCOPES)
def test_source_scope_accepts_concrete_anchor(entry):
    assert validate_source_scope([entry]) == [], f"must accept {entry!r}"


def test_source_scope_must_be_nonempty_list():
    assert validate_source_scope(None)
    assert validate_source_scope([])
    assert validate_source_scope("source://project-a/**")


def test_source_scope_rejects_mixed_valid_and_invalid():
    errors = validate_source_scope(["source://project-a/**", "source://*"])
    assert len(errors) == 1


def test_validate_boundary_accepts_base():
    assert validate_boundary(BASE_BOUNDARY) == []


def test_validate_boundary_rejects_bad_scope():
    bad = dict(BASE_BOUNDARY, source_scope=["source://*"])
    assert validate_boundary(bad)


def test_validate_boundary_rejects_missing_goal():
    bad = dict(BASE_BOUNDARY)
    del bad["task_goal"]
    assert validate_boundary(bad)
