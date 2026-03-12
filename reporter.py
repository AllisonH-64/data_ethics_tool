"""Simple reporting mechanism for infractions found in code."""

from collections import defaultdict


class Reporter:
    def __init__(self):
        self.issues = defaultdict(list)

    def report(self, filename, lineno, message):
        self.issues[filename].append((lineno, message))

    def generate(self):
        lines = []
        for fname, entries in self.issues.items():
            for lineno, msg in entries:
                lines.append(f"{fname}:{lineno}: {msg}")
        return "\n".join(lines)
