# Data Ethics & Compliance Checker

A lightweight tool designed to analyze codebases for **ethical risks** and **compliance infractions**.  
This project helps developers, educators, and organizations ensure that their code aligns with responsible data practices and regulatory standards.

---

## ✨ Features

- **Automated Scanning**: Detects potential ethical and compliance issues in code.
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
├── rules/
│   ├── __init__.py
│   ├── loader.py            # Rule loading and application engine
│   └── rule_example.py      # Example custom rule
└── tests/
    └── test_main.py         # Unit tests
```

---

## 🧪 Running Tests

```bash
.venv\Scripts\python -m pytest tests/
```

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
