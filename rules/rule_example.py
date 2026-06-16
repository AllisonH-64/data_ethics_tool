"""Example rule template. Checks for any use of `eval`, which may be problematic."""

import ast

MESSAGE = "Use of eval detected"


def check(tree: ast.AST, filename: str, reporter) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
            reporter.report(filename, node.lineno, MESSAGE)


def fix(source: str, lineno: int) -> str:
    """Replace the eval(...) call on *lineno* with a safe stub comment."""
    lines = source.splitlines(keepends=True)
    idx = lineno - 1
    if 0 <= idx < len(lines):
        indent = " " * (len(lines[idx]) - len(lines[idx].lstrip()))
        lines[idx] = indent + "# ETHICS-FIX: eval removed – replace with explicit allowlisted parsing\n"
    return "".join(lines)
