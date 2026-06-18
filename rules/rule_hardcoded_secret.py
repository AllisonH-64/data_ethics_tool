"""Detect and optionally remediate hardcoded secret assignments."""

import ast
import re

MESSAGE = "Hardcoded secret detected"
_SECRET_NAMES = (
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
)


def _is_secret_name(name: str) -> bool:
    lowered = name.lower()
    return any(marker in lowered for marker in _SECRET_NAMES)


def _env_name(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_") or "SECRET_VALUE"


def check(tree: ast.AST, filename: str, reporter) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or not _is_secret_name(target.id):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and node.value.value:
            reporter.report(filename, node.lineno, MESSAGE)


def fix(source: str, lineno: int) -> str:
    """Replace a hardcoded secret with an environment variable lookup."""
    lines = source.splitlines(keepends=True)
    idx = lineno - 1
    if not 0 <= idx < len(lines):
        return source

    line = lines[idx]
    match = re.match(r"^(?P<indent>\s*)(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=", line)
    if not match:
        return source

    indent = match.group("indent")
    name = match.group("name")
    env_name = _env_name(name)
    lines[idx] = f'{indent}{name} = os.getenv("{env_name}", "")\n'

    has_os_import = any(
        stripped.startswith("import os") or stripped.startswith("from os import")
        for stripped in (existing.strip() for existing in lines)
    )
    if not has_os_import:
        insert_at = 0
        if lines and lines[0].lstrip().startswith('"""'):
            insert_at = 1
            while insert_at < len(lines) and '"""' not in lines[insert_at]:
                insert_at += 1
            insert_at = min(insert_at + 1, len(lines))
            if insert_at < len(lines) and lines[insert_at].strip():
                lines.insert(insert_at, "\n")
                insert_at += 1
        lines.insert(insert_at, "import os\n")
    return "".join(lines)