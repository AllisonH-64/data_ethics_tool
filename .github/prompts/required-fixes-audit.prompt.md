---
description: "Run a required-fixes audit for the data ethics tool with severity-ranked findings and evidence."
name: "Required Fixes Audit"
argument-hint: "Optional scope and constraints, e.g., 'rules folder only; focus on security and test gaps'"
agent: "Required Fixes Auditor"
model: "GPT-5 (copilot)"
---
Run a required-fixes audit for this repository.

If no scope is provided in arguments, audit the whole repo.

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

3. Residual Risks
- <remaining non-blocking risks or notable test gaps>
