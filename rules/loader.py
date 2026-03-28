"""Rule loading and application utilities."""

import importlib
import os
import pkgutil
import ast
import sys


def load_rules():
    """Dynamically import all rule modules in the rules package."""
    rules = []
    package = __package__ or "rules"
    package_path = os.path.dirname(__file__)
    for finder, name, ispkg in pkgutil.iter_modules([package_path]):
        if name.startswith("rule_"):
            try:
                module = importlib.import_module(f"{package}.{name}")
            except Exception as exc:
                print(
                    f"WARNING: Failed to load rule module '{name}': {exc}",
                    file=sys.stderr,
                )
                continue
            if hasattr(module, "check") and callable(module.check):
                rules.append(module.check)
            else:
                print(
                    f"WARNING: Rule module '{name}' has no callable 'check' function and will be skipped.",
                    file=sys.stderr,
                )
    return rules


def apply_rules(filename, rules, reporter):
    """Parse a file and run all checks against its AST."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as exc:
        print(f"WARNING: Could not read '{filename}': {exc}", file=sys.stderr)
        return
    try:
        tree = ast.parse(source, filename)
    except SyntaxError as exc:
        print(
            f"WARNING: Skipping '{filename}' due to syntax error: {exc}",
            file=sys.stderr,
        )
        return
    for check in rules:
        try:
            check(tree, filename, reporter)
        except Exception as exc:
            print(
                f"WARNING: Rule '{check.__module__}.{check.__name__}' raised an error on '{filename}': {exc}",
                file=sys.stderr,
            )
