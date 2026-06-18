"""Entry point for the ethics and compliance analysis tool."""

import argparse
import os
import sys

from agentic import AgenticAnalyzer
from agent_runner import AgentRunner
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
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically apply high-confidence fixes (requires --agentic).",
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=3,
        help="Maximum perceive->act->observe iterations when --auto-fix is set.",
    )
    parser.add_argument(
        "--log",
        default=None,
        help="Write agent run log (JSON) to this file path.",
    )
    return parser.parse_args()


_SKIP_DIRS = {
    ".venv", "venv", "__pycache__", ".git", ".tox",
    "node_modules", ".mypy_cache", ".pytest_cache", "dist", "build",
}


def collect_targets(target: str) -> list:
    """Return a list of .py file paths to scan under *target*."""
    if os.path.isdir(target):
        targets = []
        for root, dirs, files in os.walk(target):
            dirs[:] = [
                d for d in dirs
                if d not in _SKIP_DIRS and not d.endswith(".egg-info")
            ]
            for f in files:
                if f.endswith(".py"):
                    targets.append(os.path.join(root, f))
        return targets
    return [target]


def main():
    args = parse_args()
    target = args.path
    rules = loader.load_rules()

    if not os.path.exists(target):
        print(f"Error: path '{target}' does not exist.", file=sys.stderr)
        sys.exit(2)

    if os.path.isfile(target) and not target.endswith(".py"):
        print(f"Error: '{target}' is not a Python file.", file=sys.stderr)
        sys.exit(2)

    targets = collect_targets(target)

    if args.agentic and args.auto_fix:
        runner = AgentRunner(
            rules=rules,
            goal=args.goal,
            max_iter=args.max_iter,
            max_actions=args.max_actions,
            auto_fix=True,
            log_path=args.log,
        )
        result = runner.run(targets, output_format=args.format)
        report = result["report"]
        has_issues = result["has_issues"]
    elif args.agentic:
        reporter = Reporter()
        for t in targets:
            loader.apply_rules(t, rules, reporter)
        analyzer = AgenticAnalyzer(goal=args.goal, max_actions=args.max_actions)
        report = analyzer.build_report(reporter.issues, output_format=args.format)
        has_issues = bool(reporter.issues)
    else:
        reporter = Reporter()
        for t in targets:
            loader.apply_rules(t, rules, reporter)
        report = reporter.generate()
        has_issues = bool(reporter.issues)

    if args.output:
        with open(args.output, "w") as out:
            out.write(report)
    else:
        print(report)

    if has_issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
