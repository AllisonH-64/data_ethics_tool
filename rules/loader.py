"""Rule loading and application utilities."""

import importlib
import os
import pkgutil
import ast
import sys
from collections import namedtuple

Rule = namedtuple("Rule", ["name", "check", "fix", "message"])


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
                rules.append(
                    Rule(
                        name=name,
                        check=module.check,
                        fix=getattr(module, "fix", None),
                        message=getattr(module, "MESSAGE", None),
                    )
                )
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
    for rule in rules:
        # Accept both Rule namedtuples and raw callables (backward compat).
        if hasattr(rule, "check"):
            check_fn = rule.check
            rule_label = rule.name
        else:
            check_fn = rule
            rule_label = f"{getattr(rule, '__module__', '?')}.{getattr(rule, '__name__', '?')}"
        try:
            check_fn(tree, filename, reporter)
        except Exception as exc:
            print(
                f"WARNING: Rule '{rule_label}' raised an error on '{filename}': {exc}",
                file=sys.stderr,
            )
