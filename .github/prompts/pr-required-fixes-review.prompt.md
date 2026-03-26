---
description: "Review only branch changes versus the default branch and list required fixes for merge decisions."
name: "PR Required Fixes Review"
argument-hint: "Optional constraints, e.g., 'prioritize security and tests'"
agent: "agent"
model: "GPT-5 (copilot)"
---
Review this branch as a pull-request candidate against the default branch.

Process:
1. Identify changed files relative to default branch (for example, main...HEAD).
2. Audit only those changed files and their directly affected behavior paths.
3. Report required fixes only (no optional improvements).

Use this output contract:
1. Required Fixes
- Severity: <Critical|High|Medium>
- Issue: <short title>
- Evidence: <path + brief proof>
- Impact: <what breaks and for whom>
- Required fix: <minimal corrective action>
- Validation: <specific test/check to confirm fix>

2. Open Questions
- <only blockers that prevent confident conclusions>

3. Merge Readiness
- Decision: <Block merge|Ready after fixes|Ready>
- Rationale: <brief>

If there are no required fixes, state that explicitly and call out residual testing risk, if any.
