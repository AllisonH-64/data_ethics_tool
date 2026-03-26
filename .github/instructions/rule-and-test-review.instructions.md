---
description: "Use when reviewing Python rule modules and tests in the data ethics tool. Focus on required-fix criteria for correctness, safety, and coverage."
name: "Rule And Test Review Criteria"
applyTo:
  - "rules/**/*.py"
  - "tests/**/*.py"
---
# Rule And Test Review Criteria

Use these criteria when analyzing files in rules and tests.

## Rules (rules/**/*.py)
- Treat rule loading failures, silent misconfiguration, and incorrect default behavior as required fixes.
- Flag input/schema assumptions that can crash rule evaluation.
- Require explicit error messages for invalid rule configuration.

## Tests (tests/**/*.py)
- Treat missing tests for critical behavior paths as required fixes when regressions would be hard to detect.
- Prioritize tests for rule loading, CLI argument handling, and report generation edge cases.
- Favor deterministic assertions over broad smoke-only tests.

## Severity Guidance
- Critical: exploitable or release-blocking behavior.
- High: high-likelihood incorrect output, crash, or policy breach.
- Medium: important reliability/coverage gaps with meaningful user impact.
