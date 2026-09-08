"""Detect hardcoded secrets in plain-text files (config, env, notes, etc.).

Unlike rule_hardcoded_secret.py, this doesn't rely on parsing Python syntax —
it scans raw lines with regular expressions, so it also covers files that
aren't valid Python: .env, .yaml, .json, .ini, .cfg, .md, .txt, and similar.

No auto-fix is provided here on purpose: rewriting a secret out of an
arbitrary config format safely (env vs. YAML vs. JSON) needs format-specific
handling, so these findings are flagged for manual review only.
"""

import re

MESSAGE = "Potential secret found in text content"

_SECRET_NAMES = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "credential",
)

_PLACEHOLDER_MARKERS = (
    "changeme",
    "change_me",
    "placeholder",
    "example",
    "redacted",
    "your_",
    "xxxx",
    "todo",
)

# key = value / key: value / key="value" — covers .env, .ini, .yaml, .json-ish lines.
_ASSIGNMENT = re.compile(
    r"""^\s*['"]?(?P<name>[A-Za-z][\w.\-]*)['"]?\s*[:=]\s*"""
    r"""['"]?(?P<value>[^'"\s#]{4,})['"]?\s*[,;]?\s*(#.*)?$"""
)

# Well-known secret formats, flagged regardless of the surrounding key name.
_KNOWN_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key ID
    re.compile(r"ghp_[A-Za-z0-9]{36}"),  # GitHub personal access token
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),  # Slack token
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),  # PEM private key
)


def _looks_like_secret_name(name: str) -> bool:
    lowered = name.lower()
    return any(marker in lowered for marker in _SECRET_NAMES)


def _looks_like_placeholder(value: str) -> bool:
    lowered = value.strip().strip("\"'").lower()
    if not lowered:
        return True
    if lowered.startswith(("<", "${", "%", "{{")):
        return True
    return any(marker in lowered for marker in _PLACEHOLDER_MARKERS)


def check_text(lines, filename, reporter) -> None:
    for lineno, line in enumerate(lines, start=1):
        if any(pattern.search(line) for pattern in _KNOWN_PATTERNS):
            reporter.report(filename, lineno, MESSAGE)
            continue
        match = _ASSIGNMENT.match(line)
        if (
            match
            and _looks_like_secret_name(match.group("name"))
            and not _looks_like_placeholder(match.group("value"))
        ):
            reporter.report(filename, lineno, MESSAGE)
