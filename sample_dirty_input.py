"""Intentionally unsafe sample file for testing the data ethics tool.

Contains one instance of each rule this tool currently checks for:
eval, exec, and a hardcoded secret.
"""

api_key = "super-secret-value"

value = 2 + 2
result = eval("value * 3")

exec("print('debug output')")

print(result)
