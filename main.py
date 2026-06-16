"""Entry point for the ethics and compliance analysis tool."""

import argparse
import os
import sys

from agentic import AgenticAnalyzer
from rules import loader
from reporter import Reporter


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze data engineering code for ethical and compliance infractions."
    )
    parser.add_argument(
        "path", help="Path to the Python file or directory to analyze."
    )
    parser.add_argument(
        "--output", help="Report output file (defaults to stdout).", default=None
    )
    parser.add_argument(
        "--agentic",
        action="store_true",
        help="Enable goal-driven, prioritized analysis output.",
    )
    parser.add_argument(
        "--goal",
        default="Identify and prioritize ethics and compliance risks.",
        help="Goal statement used by agentic mode.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format for agentic mode. Standard mode always prints plain text.",
    )
    parser.add_argument(
        "--max-actions",
        type=int,
        default=5,
        help="Maximum number of recommended actions in agentic mode.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    target = args.path
    rules = loader.load_rules()
    reporter = Reporter()
    
    if not os.path.exists(target):
        print(f"Error: path '{target}' does not exist.", file=sys.stderr)
        sys.exit(2)

    # Walk through directory or single file
    _SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", ".tox", "node_modules", ".mypy_cache", ".pytest_cache", "dist", "build", "*.egg-info"}

    if os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.endswith(".egg-info")]
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    loader.apply_rules(path, rules, reporter)
    else:
        if not target.endswith(".py"):
            print(f"Error: '{target}' is not a Python file.", file=sys.stderr)
            sys.exit(2)
        loader.apply_rules(target, rules, reporter)

    if args.agentic:
        analyzer = AgenticAnalyzer(goal=args.goal, max_actions=args.max_actions)
        report = analyzer.build_report(reporter.issues, output_format=args.format)
    else:
        report = reporter.generate()

    if args.output:
        with open(args.output, "w") as out:
            out.write(report)
    else:
        print(report)

    if reporter.issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
