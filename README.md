🔗 **[Live demo](https://dataethicstool-ibplyfkoagidcaoctdqear.streamlit.app)** — try the Quick demo buttons for an instant scan, no setup required.

# Data Ethics & Compliance Checker

A lightweight tool designed to analyze codebases for **ethical risks** and **compliance infractions**.  
This project helps developers, educators, and organizations ensure that their code aligns with responsible data practices and regulatory standards.

---

## ✨ Features

- **Automated Scanning**: Detects potential ethical and compliance issues in code.
- **Concrete Risk Rules**: Flags dynamic execution patterns like `eval` and `exec`, plus hardcoded secrets.
- **Customizable Rulesets**: Extend or modify checks to fit organizational policies.
- **Clear Reporting**: Generates easy-to-read summaries of infractions with context.
- **Developer-Friendly**: Simple CLI interface for quick integration into workflows.
- **Open & Extensible**: Built to encourage collaboration and transparency.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11  
- Git installed  
- Recommended: virtual environment for clean dependency management

### Installation

```bash
git clone https://github.com/AllisonH-64/data_ethics_tool.git
cd data_ethics_tool
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🛠️ Usage

Analyze a single file:

```bash
python main.py path/to/your_file.py
```

Analyze an entire directory:

```bash
python main.py path/to/your_project/
```

Save the report to a file:

```bash
python main.py path/to/your_project/ --output report.txt
```

Run in agentic mode with prioritized findings and recommended next actions:

```bash
python main.py path/to/your_project/ --agentic
```

Emit agentic output as JSON for automation pipelines:

```bash
python main.py path/to/your_project/ --agentic --format json
```

Run the full agent loop and auto-fix high-confidence findings in place:

```bash
python main.py path/to/your_project/ --agentic --auto-fix --log run.log.json
```

### Supported Rules

- `eval(...)`: flagged as unsafe dynamic execution and auto-fixed to a review stub comment.
- `exec(...)`: flagged as unsafe dynamic execution and auto-fixed to a review stub comment.
- Hardcoded secrets: detects assignments such as `api_key = "..."` and rewrites them to `os.getenv(...)` lookups.

### Auto-Fix Example

Before:

```python
api_key = "super-secret"
exec("print('debug')")
```

After `python main.py path/to/file.py --agentic --auto-fix`:

```python
import os

api_key = os.getenv("API_KEY", "")
# ETHICS-FIX: exec removed - replace with explicit allowlisted behavior
```

### Using as a GitHub Action

This repository is itself a reusable [composite GitHub Action](action.yml). Add it to any
repository's workflow to scan Python code on every push or pull request, with findings
shown inline on the diff and summarized on the run:

```yaml
name: Data Ethics Check

on:
  pull_request:
    branches: ["main"]

jobs:
  ethics-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: AllisonH-64/data_ethics_tool@main
        with:
          path: "."              # file or directory to scan (default: ".")
          fail-on-issues: "true" # fail the check when issues are found (default: "true")
          max-actions: "5"       # max recommended actions to include (default: "5")
```

The action exposes `total-findings`, `high`, `medium`, and `low` as outputs for use in
later steps, e.g. `${{ steps.<step-id>.outputs.total-findings }}`.

### Exit Codes

- `0`: Scan completed and no violations were found.
- `1`: Scan completed and one or more violations were found.
- `2`: Invalid input, such as a missing path or a non-Python file in single-file mode.

Warnings such as unreadable files, syntax errors, or rule-loading failures are written to stderr.

### Example Output

```text
path/to/file.py:12: Use of eval detected
```

---

## 📁 Project Structure

```text
data_ethics_tool/
├── main.py                  # Entry point — CLI argument parsing and execution
├── reporter.py              # Report generation logic
├── requirements.txt         # Python dependencies
├── TERMS_AND_CONDITIONS.md  # Usage terms and conditions
├── action.yml                # GitHub Action definition (composite action)
├── scripts/
│   └── annotate.py          # Converts JSON reports into PR annotations/summaries
├── rules/
│   ├── __init__.py
│   ├── loader.py            # Rule loading and application engine
│   ├── rule_example.py      # eval detection and auto-fix example
│   ├── rule_exec.py         # exec detection and auto-fix
│   └── rule_hardcoded_secret.py  # hardcoded secret detection and auto-fix
├── agent_runner.py          # Perceive -> act -> observe loop for agent mode
└── tests/
    └── test_main.py         # Unit tests
```

---

## 🧪 Running Tests

```bash
uv run --with pytest pytest -q
```

If you are using an activated virtual environment with dependencies installed, this also works:

```bash
python -m pytest -q
```

---

## ⚖️ Legal & Regulatory Basis

The rules in this tool are grounded in established data protection law rather than
invented conventions. Two frameworks currently inform the ruleset:

**EU General Data Protection Regulation (GDPR — Regulation (EU) 2016/679)**

- Article 5(1)(f) — *integrity and confidentiality*: personal data must be processed
"in a manner that ensures appropriate security ... including protection against
unauthorised or unlawful processing and against accidental loss, destruction or
damage." Hardcoded secrets and unreviewed `eval`/`exec` calls are exactly the kind
of avoidable exposure this principle targets.
- Article 5(2) — *accountability*: controllers must be able to demonstrate compliance,
not just claim it. Automated, repeatable scanning on every push/PR is one concrete
way to evidence that.
- Article 32 — *security of processing*: requires "appropriate technical and
organisational measures," which is the same standard this tool's secret- and
unsafe-execution checks are built to help satisfy.

**Barbados Data Protection Act, 2019‑29**

- Section 4(1) — the Act's own six data protection principles, closely mirroring
GDPR Article 5, including 4(1)(f): processing must ensure "appropriate security of
the personal data."
- Section 4(2) — places the accountability obligation on the data controller directly.
- Section 62 — *security of processing*: requires "appropriate technical and
organisational measures to ensure a level of security appropriate to the risk,"
Barbados's analogue to GDPR Article 32.
- Section 70 establishes the **Office of the Data Protection Commissioner**, the
regulator responsible for oversight and enforcement (the Act became enforceable
in 2021).

### How this maps to the current rules

| Rule | Principle it supports | GDPR | Barbados DPA |
| --- | --- | --- | --- |
| `rule_hardcoded_secret.py` | Security / integrity & confidentiality | Art. 5(1)(f), Art. 32 | s. 4(1)(f), s. 62 |
| `rule_example.py` (`eval`) | Security / integrity & confidentiality | Art. 5(1)(f), Art. 32 | s. 4(1)(f), s. 62 |
| `rule_exec.py` | Security / integrity & confidentiality | Art. 5(1)(f), Art. 32 | s. 4(1)(f), s. 62 |
| Automated scanning on every push/PR (this repo, or as a GitHub Action) | Accountability | Art. 5(2) | s. 4(2) |

> **Not legal advice.** This tool checks for a narrow set of code-level risk patterns
> and does not assess legal compliance on its own — it's a helpful signal, not a
> substitute for a data protection impact assessment or legal review. Section/article
> numbers above are provided for reference; consult the primary sources — the
> [GDPR text](https://gdpr-info.eu/) and the
> [Barbados Data Protection Act, 2019‑29 (official text)](https://oag.gov.bb/attachments/Data%20Protection%20Act,%202019-29.pdf)
> — and a qualified professional for anything you intend to rely on.

---

## 📋 Terms and Conditions

Use of this tool is subject to the [Terms and Conditions](TERMS_AND_CONDITIONS.md).

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source. See repository settings for license details.
