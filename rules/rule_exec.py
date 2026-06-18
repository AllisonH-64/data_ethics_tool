"""Detect and optionally neutralize use of exec()."""

import ast

MESSAGE = "Use of exec detected"


def check(tree: ast.AST, filename: str, reporter) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "exec":
            reporter.report(filename, node.lineno, MESSAGE)


def fix(source: str, lineno: int) -> str:
    """Replace the exec(...) line with a review stub comment."""
    lines = source.splitlines(keepends=True)
    idx = lineno - 1
    if 0 <= idx < len(lines):
        indent = " " * (len(lines[idx]) - len(lines[idx].lstrip()))
        lines[idx] = indent + "# ETHICS-FIX: exec removed - replace with explicit allowlisted behavior\n"
    return "".join(lines)