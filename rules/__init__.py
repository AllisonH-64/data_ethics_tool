# package initializer for rules
from .loader import load_rules, apply_rules, apply_text_rules, apply, TEXT_EXTENSIONS

__all__ = [
    "load_rules",
    "apply_rules",
    "apply_text_rules",
    "apply",
    "TEXT_EXTENSIONS",
]
