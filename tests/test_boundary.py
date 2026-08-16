"""P0 合同测试: boundary_hash 确定性 + hive scope fail-closed (§12.1)."""

from sanyuan_hive.boundary import assert_hive_scope, boundary_hash

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
