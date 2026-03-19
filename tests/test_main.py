"""Basic tests for the ethics compliance analyzer."""

import os
import sys

# Ensure project root is importable when tests are executed from isolated runners.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import main


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
