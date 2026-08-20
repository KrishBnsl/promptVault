"""Diff algorithm for comparing prompt versions."""

import difflib


def compute_diff(
    content_a: str,
    content_b: str,
    from_file: str = "version_a",
    to_file: str = "version_b",
) -> str:
    """Compute a unified diff between two prompt contents."""
    lines_a = content_a.splitlines(keepends=True)
    lines_b = content_b.splitlines(keepends=True)

    diff = difflib.unified_diff(
        lines_a,
        lines_b,
        fromfile=from_file,
        tofile=to_file,
    )
    return "".join(diff)


def compute_side_by_side(content_a: str, content_b: str) -> dict:
    """Compute a side-by-side comparison of two prompt contents."""
    lines_a = content_a.splitlines()
    lines_b = content_b.splitlines()

    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for line in lines_a[i1:i2]:
                result.append({"type": "equal", "line": line})
        elif tag == "replace":
            for line in lines_a[i1:i2]:
                result.append({"type": "removed", "line": line})
            for line in lines_b[j1:j2]:
                result.append({"type": "added", "line": line})
        elif tag == "delete":
            for line in lines_a[i1:i2]:
                result.append({"type": "removed", "line": line})
        elif tag == "insert":
            for line in lines_b[j1:j2]:
                result.append({"type": "added", "line": line})

    return {"changes": result}
