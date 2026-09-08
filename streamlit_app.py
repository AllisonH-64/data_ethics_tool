"""Simple web interface for the Data Ethics & Compliance Checker."""

import json
import os
import tempfile

import pandas as pd
import streamlit as st

from agent_runner import AgentRunner
from agentic import AgenticAnalyzer
from main import collect_targets
from reporter import Reporter
from rules import loader

st.set_page_config(
    page_title="Data ethics checker",
    page_icon=":material/policy:",
    layout="wide",
)

SEVERITY_COLORS = {
    "high": "background-color: rgba(239, 68, 68, 0.18)",
    "medium": "background-color: rgba(249, 115, 22, 0.18)",
    "low": "background-color: rgba(234, 179, 8, 0.18)",
}

SUPPORTED_EXTENSIONS = {".py"} | loader.TEXT_EXTENSIONS
UPLOAD_TYPES = ["py"] + sorted(ext.lstrip(".") for ext in loader.TEXT_EXTENSIONS)


def clean_path(raw: str) -> str:
    """Normalize a user-typed path: trim whitespace and surrounding quotes.

    Windows' "Copy as path" wraps paths in double quotes, and copy/paste
    often leaves trailing whitespace — both make os.path.exists() fail
    silently, so strip them before touching the filesystem.
    """
    cleaned = raw.strip().strip('"').strip("'")
    return os.path.normpath(cleaned) if cleaned else cleaned


def scan_targets(targets: list, goal: str, max_actions: int) -> dict:
    """Run all rules over *targets* and return the agentic report as a dict."""
    rules = loader.load_rules()
    reporter = Reporter()
    for target in targets:
        loader.apply(target, rules, reporter)
    analyzer = AgenticAnalyzer(goal=goal, max_actions=max_actions)
    return json.loads(analyzer.build_report(reporter.issues, output_format="json"))


def auto_fix_targets(targets: list, goal: str, max_actions: int, max_iter: int):
    """Run the perceive->act->observe loop with auto-fix enabled.

    Returns (report_dict, total_fixed_count).
    """
    rules = loader.load_rules()
    runner = AgentRunner(
        rules=rules,
        goal=goal,
        max_iter=max_iter,
        max_actions=max_actions,
        auto_fix=True,
    )
    result = runner.run(targets, output_format="json")
    total_fixed = sum(entry["auto_fixed"] for entry in runner.run_log)
    return json.loads(result["report"]), total_fixed


def render_results(report: dict, fixed_note: str = None):
    summary = report["summary"]
    with st.container(horizontal=True):
        st.metric("Total findings", summary["total_findings"], border=True)
        st.metric("High", summary["high"], border=True)
        st.metric("Medium", summary["medium"], border=True)
        st.metric("Low", summary["low"], border=True)

    if fixed_note:
        st.success(fixed_note, icon=":material/build:")

    if not report["findings"]:
        st.success("No issues found.", icon=":material/check_circle:")
        return

    with st.container(border=True):
        st.subheader("Findings")
        df = pd.DataFrame(report["findings"]).rename(
            columns={
                "file": "File",
                "line": "Line",
                "message": "Message",
                "severity": "Severity",
                "priority_score": "Priority",
                "confidence": "Confidence",
                "suggested_fix": "Suggested fix",
            }
        )
        styled = df.style.apply(
            lambda row: [SEVERITY_COLORS.get(row["Severity"], "")] * len(row), axis=1
        )
        st.dataframe(
            styled,
            column_config={
                "Confidence": st.column_config.ProgressColumn(
                    "Confidence", min_value=0, max_value=1, format="percent"
                ),
                "Suggested fix": st.column_config.TextColumn(width="large"),
                "Priority": None,
            },
            hide_index=True,
        )

    if report["recommended_actions"]:
        with st.container(border=True):
            st.subheader("Recommended actions")
            for index, action in enumerate(report["recommended_actions"], start=1):
                st.markdown(f"{index}. {action}")

    with st.expander("Raw report (JSON)", icon=":material/data_object:"):
        st.json(report)


st.title("Data ethics & compliance checker", icon=":material/policy:")
st.caption(
    "Scans Python code for unsafe execution patterns and hardcoded secrets, "
    "and scans text/config files (.env, .yaml, .json, .ini, .md, .txt, ...) "
    "for hardcoded secrets."
)

with st.sidebar:
    st.header("Scan target")
    source_mode = st.segmented_control(
        "Source",
        ["Local path", "Upload file", "Paste code"],
        default="Local path",
    )

    st.header("Options")
    goal = st.text_input(
        "Goal", value="Identify and prioritize ethics and compliance risks."
    )
    max_actions = st.slider("Max recommended actions", 1, 10, 5)
    enable_auto_fix = st.checkbox(
        "Auto-fix high-confidence findings",
        help=(
            "Rewrites matching files in place (eval/exec calls, hardcoded "
            "secrets). Only applies when scanning a local path."
        ),
    )
    max_iter = 3
    if enable_auto_fix:
        max_iter = st.slider("Max fix iterations", 1, 5, 3)

uploaded_files = None
code = None
path = None
paste_extension = ".py"

if source_mode == "Upload file":
    uploaded_files = st.file_uploader(
        "Upload one or more files (.py or a text/config file)",
        type=UPLOAD_TYPES,
        accept_multiple_files=True,
    )
    if enable_auto_fix:
        st.caption(
            "Auto-fix is ignored for uploaded files — switch to Local path "
            "to write fixes to disk."
        )
elif source_mode == "Paste code":
    paste_kind = st.segmented_control(
        "Content type", ["Python code", "Text / config"], default="Python code"
    )
    paste_extension = ".py" if paste_kind == "Python code" else ".txt"
    placeholder = (
        "def example():\n    ..."
        if paste_extension == ".py"
        else "api_key = 12345abcde\npassword: hunter2"
    )
    code = st.text_area("Content to scan", height=320, placeholder=placeholder)
    if enable_auto_fix:
        st.caption(
            "Auto-fix is ignored for pasted content — switch to Local path "
            "to write fixes to disk."
        )
else:
    raw_path = st.text_input(
        "Path to file or directory",
        value=".",
        help="Relative to where the app was launched, or an absolute path.",
    )
    path = clean_path(raw_path)

run_clicked = st.button("Run scan", icon=":material/play_arrow:", type="primary")

if run_clicked:
    targets = []
    error = None
    temp_dir = None

    if source_mode == "Local path":
        if not path or not os.path.exists(path):
            error = f"Path not found: `{os.path.abspath(path or raw_path)}`"
        elif os.path.isfile(path) and os.path.splitext(path)[1] not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            error = f"'{path}' is not a supported file type (expected one of: {supported})."
        else:
            targets = collect_targets(path)
    elif source_mode == "Upload file":
        if not uploaded_files:
            error = "Upload at least one file first."
        else:
            temp_dir = tempfile.TemporaryDirectory()
            for uploaded in uploaded_files:
                temp_path = os.path.join(temp_dir.name, uploaded.name)
                with open(temp_path, "wb") as fh:
                    fh.write(uploaded.getvalue())
                targets.append(temp_path)
    else:
        if not code or not code.strip():
            error = "Paste some content first."
        else:
            temp_dir = tempfile.TemporaryDirectory()
            temp_path = os.path.join(temp_dir.name, f"pasted_snippet{paste_extension}")
            with open(temp_path, "w", encoding="utf-8") as fh:
                fh.write(code)
            targets = [temp_path]

    if error:
        st.error(error, icon=":material/error:")
        st.session_state.pop("report", None)
    elif not targets:
        st.warning(
            "No supported files found at that path.", icon=":material/warning:"
        )
        st.session_state.pop("report", None)
    else:
        with st.spinner("Scanning..."):
            if enable_auto_fix and source_mode == "Local path":
                report, total_fixed = auto_fix_targets(
                    targets, goal, max_actions, max_iter
                )
                fixed_note = (
                    f"Auto-fixed {total_fixed} finding(s) in place — review "
                    "with `git diff` before committing."
                    if total_fixed
                    else None
                )
            else:
                report = scan_targets(targets, goal, max_actions)
                fixed_note = None
        st.session_state["report"] = report
        st.session_state["fixed_note"] = fixed_note

    if temp_dir:
        temp_dir.cleanup()

if "report" in st.session_state:
    render_results(st.session_state["report"], st.session_state.get("fixed_note"))
