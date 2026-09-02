"""Turn an agentic JSON report into GitHub Actions annotations and a step summary.

Reads the JSON report produced by ``main.py --agentic --format json`` and:

- Emits ``::error``/``::warning`` workflow commands so findings show up as
  inline PR annotations on the offending line.
- Writes a Markdown findings table to ``$GITHUB_STEP_SUMMARY``.
- Writes summary counts to ``$GITHUB_OUTPUT`` for downstream steps.
"""

import json
import os
import sys


def _normalize_path(path: str) -> str:
    """Make a scanned file path relative-looking, as GitHub expects for annotations."""
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _escape(message: str) -> str:
    """Escape text for use inside a GitHub Actions workflow command."""
    return message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: annotate.py <path-to-json-report>", file=sys.stderr)
        return 2

    report_path = sys.argv[1]
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"::warning::Could not read ethics report at '{report_path}': {exc}")
        return 0

    findings = report.get("findings", [])
    summary = report.get("summary", {})

    for finding in findings:
        file_path = _normalize_path(finding.get("file", ""))
        line = finding.get("line", 1)
        message = finding.get("message", "Issue detected")
        severity = finding.get("severity", "medium")
        level = "error" if severity == "high" else "warning"
        print(
            f"::{level} file={file_path},line={line},title=Data Ethics::{_escape(message)}"
        )

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        lines = ["## Data Ethics & Compliance Report", ""]
        total = summary.get("total_findings", len(findings))
        if total == 0:
            lines.append("No issues found. ✅")
        else:
            lines.append(
                f"**{total} finding(s)** "
                f"(high={summary.get('high', 0)}, "
                f"medium={summary.get('medium', 0)}, "
                f"low={summary.get('low', 0)})"
            )
            lines.append("")
            lines.append("| Severity | File | Line | Message |")
            lines.append("|---|---|---|---|")
            for finding in findings:
                lines.append(
                    f"| {finding.get('severity', '')} "
                    f"| {_normalize_path(finding.get('file', ''))} "
                    f"| {finding.get('line', '')} "
                    f"| {finding.get('message', '')} |"
                )
            actions = report.get("recommended_actions", [])
            if actions:
                lines.append("")
                lines.append("**Recommended actions:**")
                for action in actions:
                    lines.append(f"- {action}")
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"total-findings={summary.get('total_findings', len(findings))}\n")
            f.write(f"high={summary.get('high', 0)}\n")
            f.write(f"medium={summary.get('medium', 0)}\n")
            f.write(f"low={summary.get('low', 0)}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
