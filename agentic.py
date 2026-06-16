"""Agentic reporting layer for ethics and compliance findings."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class Finding:
    filename: str
    line: int
    message: str
    severity: str
    priority_score: int
    confidence: float  # 0.0 – 1.0; governs auto-fix eligibility


class AgenticAnalyzer:
    """Transforms raw findings into prioritized, goal-oriented outputs."""

    def __init__(self, goal: str, max_actions: int = 5):
        self.goal = goal
        self.max_actions = max(1, max_actions)

    def _classify(self, message: str) -> Tuple[str, int, float]:
        lowered = message.lower()
        if "eval" in lowered or "exec" in lowered:
            return "high", 100, 0.95
        if "hardcoded" in lowered or "secret" in lowered:
            return "high", 90, 0.90
        if "pii" in lowered or "privacy" in lowered:
            return "medium", 70, 0.75
        if "deprecated" in lowered:
            return "low", 40, 0.80
        return "medium", 60, 0.65

    def _flatten(self, issues: Dict[str, Iterable[Tuple[int, str]]]) -> List[Finding]:
        findings: List[Finding] = []
        for filename, entries in issues.items():
            for line, message in entries:
                severity, score, confidence = self._classify(message)
                findings.append(
                    Finding(
                        filename=filename,
                        line=line,
                        message=message,
                        severity=severity,
                        priority_score=score,
                        confidence=confidence,
                    )
                )
        findings.sort(
            key=lambda item: (-item.priority_score, item.filename.lower(), item.line)
        )
        return findings

    def _recommend_actions(self, findings: List[Finding]) -> List[str]:
        grouped = Counter(f.message for f in findings)
        actions: List[str] = []
        for message, count in grouped.most_common(self.max_actions):
            lower = message.lower()
            if "eval" in lower or "exec" in lower:
                action = "Replace dynamic execution patterns with explicit allowlisted parsing."
            elif "secret" in lower or "hardcoded" in lower:
                action = "Move sensitive values to environment variables or a secret manager."
            elif "pii" in lower or "privacy" in lower:
                action = "Add data minimization and redaction checks before processing user data."
            else:
                action = "Review this pattern and add a project-specific mitigation rule."
            actions.append(f"{action} (matches: {count})")
        return actions

    def build_report(self, issues: Dict[str, Iterable[Tuple[int, str]]], output_format: str):
        findings = self._flatten(issues)
        if output_format == "json":
            payload = {
                "goal": self.goal,
                "summary": {
                    "total_findings": len(findings),
                    "high": sum(1 for f in findings if f.severity == "high"),
                    "medium": sum(1 for f in findings if f.severity == "medium"),
                    "low": sum(1 for f in findings if f.severity == "low"),
                },
                "findings": [
                    {
                        "file": f.filename,
                        "line": f.line,
                        "message": f.message,
                        "severity": f.severity,
                        "priority_score": f.priority_score,
                        "confidence": f.confidence,
                    }
                    for f in findings
                ],
                "recommended_actions": self._recommend_actions(findings),
            }
            return json.dumps(payload, indent=2)

        lines: List[str] = [f"Agent Goal: {self.goal}"]
        if not findings:
            lines.append("Status: No issues found.")
            return "\n".join(lines)

        lines.append(
            "Summary: "
            f"{len(findings)} findings "
            f"(high={sum(1 for f in findings if f.severity == 'high')}, "
            f"medium={sum(1 for f in findings if f.severity == 'medium')}, "
            f"low={sum(1 for f in findings if f.severity == 'low')})"
        )
        lines.append("Prioritized Findings:")
        for finding in findings:
            lines.append(
                f"- [{finding.severity.upper()}] {finding.filename}:{finding.line}: {finding.message}"
            )

        lines.append("Recommended Actions:")
        for index, action in enumerate(self._recommend_actions(findings), start=1):
            lines.append(f"{index}. {action}")
        return "\n".join(lines)
