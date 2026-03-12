"""Rule loading and application utilities."""

import importlib
import os
import pkgutil
import ast


def load_rules():
    """Dynamically import all rule modules in the rules package."""
    rules = []
    package = __name__
    package_path = os.path.dirname(__file__)
    for finder, name, ispkg in pkgutil.iter_modules([package_path]):
        if name.startswith("rule_"):
            module = importlib.import_module(f"{package}.{name}")
            if hasattr(module, "check"):
                rules.append(module.check)
    return rules


def apply_rules(filename, rules, reporter):
    """Parse a file and run all checks against its AST."""
    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename)
    for check in rules:
        check(tree, filename, reporter)
