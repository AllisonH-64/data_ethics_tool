"""Entry point for the ethics and compliance analysis tool."""

import argparse
import os
import sys

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
    if os.path.isdir(target):
        for root, _, files in os.walk(target):
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    loader.apply_rules(path, rules, reporter)
    else:
        if not target.endswith(".py"):
            print(f"Error: '{target}' is not a Python file.", file=sys.stderr)
            sys.exit(2)
        loader.apply_rules(target, rules, reporter)

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
