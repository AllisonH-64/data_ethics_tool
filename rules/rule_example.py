"""Example rule template. Checks for any use of `eval`, which may be problematic."""

import ast


def check(tree: ast.AST, filename: str, reporter):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
            reporter.report(filename, node.lineno, "Use of eval detected")
