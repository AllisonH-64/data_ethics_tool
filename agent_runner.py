"""Goal-driven agent that scans, prioritises, and optionally auto-fixes findings."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from agentic import AgenticAnalyzer, Finding
from reporter import Reporter
from rules import loader as rule_loader

# Findings with confidence >= this threshold are eligible for auto-fix.
_AUTO_FIX_CONFIDENCE = 0.85


class AgentRunner:
    """Perceive → act → observe loop over a set of target files.

    Parameters
    ----------
    rules:
        List of Rule namedtuples returned by ``loader.load_rules()``.
    goal:
        Plain-language goal passed to AgenticAnalyzer for report headers.
    max_iter:
        Hard cap on perceive→act→observe iterations.
    max_actions:
        Maximum recommended actions included in the report.
    auto_fix:
        When True, high-confidence findings are rewritten in place.
    log_path:
        Optional file path; each iteration's summary is appended as JSON.
    """

    def __init__(
        self,
        rules: list,
        goal: str,
        max_iter: int = 3,
        max_actions: int = 5,
        auto_fix: bool = False,
        log_path: Optional[str] = None,
    ) -> None:
        self.rules = rules
        self.analyzer = AgenticAnalyzer(goal=goal, max_actions=max_actions)
        self.max_iter = max(1, max_iter)
        self.auto_fix = auto_fix
        self.log_path = log_path
        self.run_log: List[Dict] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _scan(self, targets: List[str]):
        """Run all rules over *targets* and return (reporter, sorted findings)."""
        reporter = Reporter()
        for target in targets:
            rule_loader.apply_rules(target, self.rules, reporter)
        findings = self.analyzer._flatten(reporter.issues)
        return reporter, findings

    def _find_fix(self, message: str):
        """Return the fix function for the rule that produced *message*, or None."""
        for rule in self.rules:
            if (
                hasattr(rule, "fix")
                and rule.fix is not None
                and hasattr(rule, "message")
                and rule.message is not None
                and rule.message in message
            ):
                return rule.fix
        return None

    def _apply_fixes(self, findings: List[Finding]):
        """Attempt to auto-fix each eligible finding in place.

        Returns ``(fixed, skipped)`` lists.
        """
        fixed, skipped = [], []
        for f in findings:
            if f.confidence < _AUTO_FIX_CONFIDENCE:
                skipped.append(f)
                continue
            fix_fn = self._find_fix(f.message)
            if fix_fn is None:
                skipped.append(f)
                continue
            try:
                with open(f.filename, "r", encoding="utf-8") as fh:
                    source = fh.read()
                patched = fix_fn(source, f.line)
                with open(f.filename, "w", encoding="utf-8") as fh:
                    fh.write(patched)
                fixed.append(f)
            except OSError:
                skipped.append(f)
        return fixed, skipped

    def _write_log(
        self,
        iteration: int,
        findings: List[Finding],
        fixed: List[Finding],
        skipped: List[Finding],
    ) -> None:
        entry = {
            "iteration": iteration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "findings": len(findings),
            "auto_fixed": len(fixed),
            "no_fix_available": len(skipped),
        }
        self.run_log.append(entry)
        if self.log_path:
            try:
                with open(self.log_path, "w", encoding="utf-8") as fh:
                    json.dump(self.run_log, fh, indent=2)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, targets: List[str], output_format: str = "text") -> Dict:
        """Execute the perceive → act → observe loop.

        Returns a dict with:
          ``report``     – formatted report string
          ``has_issues`` – True if findings remain after all iterations
        """
        total_fixed: List[Finding] = []

        for iteration in range(1, self.max_iter + 1):
            _, findings = self._scan(targets)

            if not findings:
                self._write_log(iteration, [], [], [])
                break

            if self.auto_fix:
                fixed, skipped = self._apply_fixes(findings)
                total_fixed.extend(fixed)
                self._write_log(iteration, findings, fixed, skipped)
                if not fixed:
                    # Nothing new was fixable; stop to avoid an infinite loop.
                    break
            else:
                self._write_log(iteration, findings, [], findings)
                break  # Single-pass when not auto-fixing.

        # Final scan for the conclusive report.
        final_reporter, final_findings = self._scan(targets)
        report = self.analyzer.build_report(
            final_reporter.issues, output_format=output_format
        )

        if self.auto_fix and total_fixed and output_format == "text":
            report += (
                f"\nAgent applied {len(total_fixed)} auto-fix(es) "
                f"across {len(self.run_log)} iteration(s)."
            )

        return {
            "report": report,
            "has_issues": bool(final_findings),
        }
