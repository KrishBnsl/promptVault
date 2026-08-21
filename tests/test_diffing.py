"""Tests for prompt diffing."""

from core.diffing import compute_diff, compute_side_by_side


def test_unified_diff():
    diff = compute_diff("one\ntwo\n", "one\nthree\n", "v1", "v2")

    assert "--- v1" in diff
    assert "+++ v2" in diff
    assert "-two" in diff
    assert "+three" in diff


def test_side_by_side_covers_change_types():
    comparison = compute_side_by_side("same\nold\ndelete", "same\nnew\nadd")
    types = {change["type"] for change in comparison["changes"]}

    assert types == {"equal", "removed", "added"}
