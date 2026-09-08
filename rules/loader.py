"""Rule loading and application utilities."""

import importlib
import os
import pkgutil
import ast
import sys
from collections import namedtuple

Rule = namedtuple("Rule", ["name", "check", "check_text", "fix", "message"])

# Non-Python file extensions scanned with text-based (regex) rules instead
# of the Python AST. Kept here so main.py and the web interface share one
# definition of what counts as a "supported text file".
TEXT_EXTENSIONS = {
    ".txt", ".md", ".env", ".yaml", ".yml",
    ".json", ".ini", ".cfg", ".conf", ".properties",
}


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
            has_check = hasattr(module, "check") and callable(module.check)
            has_check_text = hasattr(module, "check_text") and callable(module.check_text)
            if has_check or has_check_text:
                rules.append(
                    Rule(
                        name=name,
                        check=module.check if has_check else None,
                        check_text=module.check_text if has_check_text else None,
                        fix=getattr(module, "fix", None),
                        message=getattr(module, "MESSAGE", None),
                    )
                )
            else:
                print(
                    f"WARNING: Rule module '{name}' has no callable 'check' or "
                    "'check_text' function and will be skipped.",
                    file=sys.stderr,
                )
    return rules


def apply_rules(filename, rules, reporter):
    """Parse a Python file and run all AST-based checks against it."""
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
        if check_fn is None:
            continue
        try:
            check_fn(tree, filename, reporter)
        except Exception as exc:
            print(
                f"WARNING: Rule '{rule_label}' raised an error on '{filename}': {exc}",
                file=sys.stderr,
            )


def apply_text_rules(filename, rules, reporter):
    """Read a non-Python text file and run text-based (regex) checks against it.

    Files in TEXT_EXTENSIONS aren't valid Python, so they can't go through
    ast.parse — rules here get the raw lines instead of an AST.
    """
    try:
        with open(filename, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as exc:
        print(f"WARNING: Could not read '{filename}': {exc}", file=sys.stderr)
        return
    for rule in rules:
        check_fn = getattr(rule, "check_text", None)
        if check_fn is None:
            continue
        rule_label = getattr(rule, "name", "?")
        try:
            check_fn(lines, filename, reporter)
        except Exception as exc:
            print(
                f"WARNING: Rule '{rule_label}' raised an error on '{filename}': {exc}",
                file=sys.stderr,
            )


def apply(filename, rules, reporter):
    """Scan *filename*, dispatching to AST or text-based rules by extension."""
    if filename.endswith(".py"):
        apply_rules(filename, rules, reporter)
    else:
        apply_text_rules(filename, rules, reporter)
