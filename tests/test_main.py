"""Basic tests for the ethics compliance analyzer."""

import os
import sys

# Ensure project root is importable when tests are executed from isolated runners.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from main import main
from rules import loader
from reporter import Reporter


def _run_main(argv, monkeypatch):
    monkeypatch.setattr(sys, "argv", [sys.argv[0]] + argv)
    main()


def test_analysis(tmp_path, capsys):
    # create a simple python file with eval
    file = tmp_path / "sample.py"
    file.write_text("eval('2+2')\n")

    main_args = [str(file)]
    # monkeypatch sys.argv
    sys_argv = sys.argv
    sys.argv = [sys.argv[0]] + main_args
    try:
        main()
        captured = capsys.readouterr()
        assert "eval" in captured.out
    finally:
        sys.argv = sys_argv


def test_analysis_output_format(tmp_path, monkeypatch, capsys):
    """Output must include filename, line number, and message."""
    file = tmp_path / "check.py"
    file.write_text("eval('x')\n")
    _run_main([str(file)], monkeypatch)
    out = capsys.readouterr().out
    assert str(file) in out
    assert ":1:" in out
    assert "eval" in out


def test_no_issues_produces_no_output(tmp_path, monkeypatch, capsys):
    """A file with no violations should produce no output."""
    file = tmp_path / "clean.py"
    file.write_text("x = 1 + 1\n")
    _run_main([str(file)], monkeypatch)
    out = capsys.readouterr().out.strip()
    assert out == ""


def test_syntax_error_file_is_skipped(tmp_path, monkeypatch, capsys):
    """A file with invalid syntax should be skipped without crashing."""
    file = tmp_path / "bad.py"
    file.write_text("def foo(\n")
    _run_main([str(file)], monkeypatch)
    # No crash — stdout should have no issue lines for this file
    out = capsys.readouterr().out
    assert str(file) not in out


def test_empty_file_is_handled(tmp_path, monkeypatch, capsys):
    """An empty file should produce no output and not crash."""
    file = tmp_path / "empty.py"
    file.write_text("")
    _run_main([str(file)], monkeypatch)
    out = capsys.readouterr().out.strip()
    assert out == ""


def test_directory_traversal(tmp_path, monkeypatch, capsys):
    """All .py files in a directory tree should be analyzed."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "a.py").write_text("eval('a')\n")
    (sub / "b.py").write_text("eval('b')\n")
    _run_main([str(tmp_path)], monkeypatch)
    out = capsys.readouterr().out
    assert "a.py" in out
    assert "b.py" in out


def test_output_to_file(tmp_path, monkeypatch):
    """--output flag should write report to a file instead of stdout."""
    src = tmp_path / "src.py"
    src.write_text("eval('x')\n")
    out_file = tmp_path / "report.txt"
    _run_main([str(src), "--output", str(out_file)], monkeypatch)
    assert out_file.exists()
    content = out_file.read_text()
    assert "eval" in content


def test_load_rules_warns_on_import_error(tmp_path, monkeypatch, capsys):
    """load_rules should warn to stderr when a rule module cannot be imported."""
    import importlib
    import pkgutil

    broken_rule = tmp_path / "rule_broken.py"
    broken_rule.write_text("raise ImportError('intentional')\n")

    original_iter = pkgutil.iter_modules

    def patched_iter(path):
        yield from original_iter(path)
        # Inject a fake module name that will fail to import
        import pkgutil as _pk
        class FakeFinder:
            pass
        yield FakeFinder(), "rule_broken", False

    monkeypatch.setattr(pkgutil, "iter_modules", patched_iter)
    # Point the rules package path to tmp_path so rule_broken is discoverable
    import rules.loader as rl
    monkeypatch.setattr(rl, "__package__", "rules")

    import sys as _sys
    _sys.path.insert(0, str(tmp_path))
    try:
        # This will attempt to import 'rules.rule_broken' which won't resolve,
        # so the WARNING should appear in stderr.
        loader.load_rules()
        err = capsys.readouterr().err
        assert "WARNING" in err
    finally:
        _sys.path.remove(str(tmp_path))


def test_load_rules_warns_on_missing_check(tmp_path, monkeypatch, capsys):
    """load_rules should warn when a rule module has no callable check."""
    import pkgutil

    original_iter = pkgutil.iter_modules

    # Create a real module in sys.modules with no check attribute
    import types
    fake_module = types.ModuleType("rules.rule_noop")
    sys.modules["rules.rule_noop"] = fake_module

    def patched_iter(path):
        yield from original_iter(path)
        class FakeFinder:
            pass
        yield FakeFinder(), "rule_noop", False

    monkeypatch.setattr(pkgutil, "iter_modules", patched_iter)

    try:
        loader.load_rules()
        err = capsys.readouterr().err
        assert "WARNING" in err
        assert "rule_noop" in err
    finally:
        del sys.modules["rules.rule_noop"]


def test_apply_rules_handles_crashing_rule(tmp_path, capsys):
    """A rule that raises an exception should be caught and warned, not propagate."""
    file = tmp_path / "file.py"
    file.write_text("x = 1\n")

    def bad_check(tree, filename, reporter):
        raise RuntimeError("rule crashed")

    rep = Reporter()
    loader.apply_rules(str(file), [bad_check], rep)
    err = capsys.readouterr().err
    assert "WARNING" in err
    assert "rule crashed" in err
