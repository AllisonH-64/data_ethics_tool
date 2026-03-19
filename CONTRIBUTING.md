# Contributing Guide

Thanks for contributing to this project.

## Development Setup

1. Fork and clone the repository.
2. Create a virtual environment.
3. Install dependencies.

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
pip install pytest
```

## Running Tests

```bash
python -m pytest tests/
```

## Coding Guidelines

- Keep changes focused and small.
- Add or update tests for behavior changes.
- Prefer clear, maintainable code over clever shortcuts.
- Keep documentation in sync with code changes.

## Pull Request Process

1. Create a branch from main.
2. Make your changes and run tests locally.
3. Commit with a clear message.
4. Open a pull request with:
   - What changed
   - Why it changed
   - How it was tested

## Reporting Bugs

Open an issue and include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Error output (if available)
