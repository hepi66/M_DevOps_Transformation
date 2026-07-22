import html
import json
import os
import re
import shutil
import subprocess  # nosec B404 - required for controlled Git/GitHub CLI commands
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from dashboard.formatting import format_dashboard_timestamp
from dashboard.layout import render_component_header


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

EVENT_STATE_STYLES = {
    "INFO": ("ℹ", "blue"),
    "QUEUED": ("◷", "gray"),
    "PENDING": ("◷", "gray"),
    "RUNNING": ("▶", "blue"),
    "SUCCESS": ("✓", "green"),
    "HEALTHY": ("✓", "green"),
    "WARNING": ("⚠", "orange"),
    "FAILED": ("✕", "red"),
    "ATTENTION REQUIRED": ("✕", "red"),
    "CANCELLED": ("—", "gray"),
    "SKIPPED": ("—", "gray"),
    "UNKNOWN": ("?", "gray"),
    "NOT AVAILABLE": ("?", "gray"),
}

EVENT_ICON_COLORS = {
    "ℹ": "#0054a3",
    "◷": "#6b7280",
    "▶": "#0054a3",
    "✓": "#158237",
    "⚠": "#d97706",
    "✕": "#dc2626",
    "—": "#6b7280",
    "?": "#6b7280",
}


def _find_gh_executable() -> str | None:
    executable = shutil.which("gh")
    if executable:
        return executable

    candidates = []
    if os.environ.get("ProgramFiles"):
        candidates.append(
            Path(os.environ["ProgramFiles"]) / "GitHub CLI" / "gh.exe"
        )
    if os.environ.get("LOCALAPPDATA"):
        candidates.extend(
            [
                Path(os.environ["LOCALAPPDATA"])
                / "Programs"
                / "GitHub CLI"
                / "gh.exe",
                Path(os.environ["LOCALAPPDATA"])
                / "Microsoft"
                / "WinGet"
                / "Links"
                / "gh.exe",
            ]
        )

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    return None


def _run_git_command(*arguments: str) -> str | None:
    try:
        result = subprocess.run(  # nosec B603 B607 - fixed local Git command
            ["git", *arguments],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def _run_gh_command(*arguments: str) -> str | None:
    executable = _find_gh_executable()
    if executable is None:
        return None

    try:
        result = subprocess.run(  # nosec B603 B607 - fixed read-only GitHub CLI
            [executable, *arguments],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def _run_gh_json(*arguments: str) -> Any | None:
    output = _run_gh_command(*arguments)
    if not output:
        return None

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


def _get_synchronization_state() -> str:
    upstream = _run_git_command(
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )

    if not upstream:
        return "Not available locally"

    counts = _run_git_command(
        "rev-list",
        "--left-right",
        "--count",
        f"HEAD...{upstream}",
    )

    if not counts:
        return "Not available locally"

    try:
        ahead, behind = (int(value) for value in counts.split())
    except ValueError:
        return "Not available locally"

    if ahead == 0 and behind == 0:
        return f"In sync with {upstream}"

    return f"Ahead {ahead}, behind {behind} compared with {upstream}"


def _classify_github_status(
    workflow_status: str | None,
    workflow_conclusion: str | None,
    check_state: str | None = None,
) -> str:
    failure_states = {
        "action_required",
        "cancelled",
        "failure",
        "startup_failure",
        "timed_out",
    }
    running_states = {
        "expected",
        "in_progress",
        "pending",
        "queued",
        "requested",
        "waiting",
    }

    normalized_check = (check_state or "").lower()
    normalized_status = (workflow_status or "").lower()
    normalized_conclusion = (workflow_conclusion or "").lower()

    if normalized_check in failure_states or normalized_conclusion in failure_states:
        return "Attention required"

    if normalized_check in running_states or normalized_status in running_states:
        return "Running"

    if normalized_status == "completed" and normalized_conclusion in {
        "neutral",
        "skipped",
        "success",
    }:
        return "Healthy"

    return "Not available"


def _get_check_details(pull_request: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not pull_request:
        return None, None

    checks = pull_request.get("statusCheckRollup") or []
    running_states = {"EXPECTED", "IN_PROGRESS", "PENDING", "QUEUED", "REQUESTED", "WAITING"}
    failure_states = {"ACTION_REQUIRED", "CANCELLED", "FAILURE", "STARTUP_FAILURE", "TIMED_OUT"}

    for check in checks:
        conclusion = str(check.get("conclusion") or "").upper()
        state = str(check.get("state") or check.get("status") or "").upper()
        if conclusion in failure_states or state in failure_states:
            return "failure", check.get("name") or check.get("context")

    for check in checks:
        state = str(check.get("state") or check.get("status") or "").upper()
        if state in running_states:
            return "pending", None

    return None, None


def _workflow_event_state(conclusion: str | None) -> str:
    states = {
        "cancelled": "CANCELLED",
        "failure": "FAILED",
        "neutral": "UNKNOWN",
        "skipped": "SKIPPED",
        "success": "SUCCESS",
        "timed_out": "FAILED",
    }
    return states.get((conclusion or "").lower(), "UNKNOWN")


def _render_event_timeline(events: list[dict[str, str]]) -> None:
    rows = [
        """
<style>
.operational-event-timeline {
    height: 210px;
    overflow: auto;
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 0.5rem;
    padding: 0.2rem 0.45rem;
}
.operational-event-timeline .event-row {
    display: grid;
    grid-template-columns: 6.8rem 1.4rem 1.2rem max-content;
    min-width: 100%;
    width: max-content;
    align-items: center;
    column-gap: 0.35rem;
    min-height: 34px;
    border-bottom: 1px solid rgba(128, 128, 128, 0.14);
    font-size: 0.82rem;
}
.operational-event-timeline .event-row:last-child {
    border-bottom: 0;
}
.operational-event-timeline .event-time {
    white-space: nowrap;
    font-family: monospace;
    font-variant-numeric: tabular-nums;
}
.operational-event-timeline .event-state {
    white-space: nowrap;
    text-align: center;
    font-weight: 700;
}
.operational-event-timeline .event-source {
    white-space: nowrap;
    text-align: center;
    font-family: monospace;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: rgba(128, 128, 128, 0.95);
}
.operational-event-timeline .event-subject {
    white-space: nowrap;
}
</style>
<div class="operational-event-timeline" role="table" aria-label="Recent operational events">
"""
    ]

    for event in events:
        icon, _ = EVENT_STATE_STYLES.get(
            event.get("state", "UNKNOWN").upper(),
            EVENT_STATE_STYLES["UNKNOWN"],
        )
        timestamp = html.escape(format_dashboard_timestamp(event.get("timestamp")))
        subject = html.escape(
            event.get("subject") or event.get("description") or "Event",
            quote=True,
        )
        state = html.escape(event.get("state", "UNKNOWN").replace("_", " ").title())
        color = EVENT_ICON_COLORS.get(icon, EVENT_ICON_COLORS["?"])
        rows.append(
            f'<div class="event-row" role="row">'
            f'<span class="event-time" role="cell">{timestamp}</span>'
            f'<span class="event-source" role="cell">'
            f'{html.escape(event.get("source", "--"))}</span>'
            f'<span class="event-state" role="cell" aria-label="{state}" '
            f'style="color: {color}">{icon}</span>'
            f'<span class="event-subject" role="cell" title="{subject}">{subject}</span>'
            "</div>"
        )

    rows.append("</div>")
    st.html("\n".join(rows))


def _build_operational_events(
    runs: list[dict[str, Any]],
) -> list[dict[str, str]]:
    events = []

    for run in runs:
        workflow_name = run.get("name") or "Workflow"
        if run.get("startedAt"):
            events.append(
                {
                    "timestamp": run["startedAt"],
                    "source": "CI",
                    "subject": workflow_name,
                    "state": "RUNNING",
                }
            )

        if run.get("status") == "completed" and run.get("updatedAt"):
            events.append(
                {
                    "timestamp": run["updatedAt"],
                    "source": "CI",
                    "subject": workflow_name,
                    "state": _workflow_event_state(run.get("conclusion")),
                }
            )
        elif run.get("createdAt") and not run.get("startedAt"):
            events.append(
                {
                    "timestamp": run["createdAt"],
                    "source": "CI",
                    "subject": workflow_name,
                    "state": "QUEUED",
                }
            )

    return sorted(events, key=lambda event: event["timestamp"], reverse=True)[:10]


@st.cache_data(ttl=60, show_spinner=False)
def _load_github_status() -> dict[str, Any]:
    remote = _run_git_command("remote", "get-url", "origin")
    if not remote or "github.com" not in remote.lower():
        return {"state": "Not available", "reason": "GitHub remote is unavailable."}

    if _run_gh_command("auth", "status") is None:
        return {
            "state": "Not available",
            "reason": "GitHub CLI is unavailable or not authenticated.",
        }

    repository = _run_gh_json("repo", "view", "--json", "nameWithOwner,url")
    branch = _run_git_command("branch", "--show-current")
    if not isinstance(repository, dict) or not branch:
        return {"state": "Not available", "reason": "GitHub repository could not be resolved."}

    runs = _run_gh_json(
        "run",
        "list",
        "--branch",
        branch,
        "--limit",
        "5",
        "--json",
        "databaseId,name,status,conclusion,createdAt,startedAt,updatedAt,url,headBranch",
    )
    workflow = runs[0] if isinstance(runs, list) and runs else None

    pull_requests = _run_gh_json(
        "pr",
        "list",
        "--head",
        branch,
        "--state",
        "open",
        "--limit",
        "1",
        "--json",
        "number,title,reviewDecision,mergeStateStatus,url,createdAt,updatedAt,statusCheckRollup",
    )
    pull_request = (
        pull_requests[0]
        if isinstance(pull_requests, list) and pull_requests
        else None
    )
    check_state, failed_check = _get_check_details(pull_request)

    workflow_status = workflow.get("status") if workflow else None
    workflow_conclusion = workflow.get("conclusion") if workflow else None
    state = _classify_github_status(
        workflow_status,
        workflow_conclusion,
        check_state,
    )

    latest_update = None
    if workflow:
        latest_update = workflow.get("updatedAt")
    if pull_request and pull_request.get("updatedAt"):
        latest_update = max(latest_update or "", pull_request["updatedAt"])

    return {
        "state": state,
        "repository": repository.get("nameWithOwner"),
        "branch": branch,
        "workflow": workflow,
        "pull_request": pull_request,
        "failed_check": failed_check,
        "last_update": latest_update,
        "url": (
            (pull_request or {}).get("url")
            or (workflow or {}).get("url")
            or repository.get("url")
        ),
        "events": _build_operational_events(
            runs if isinstance(runs, list) else [],
        ),
    }


def _snapshot_timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def _format_git_commit_subject(commit_hash: str, commit_message: str) -> str:
    pull_request_merge = re.fullmatch(
        r"Merge pull request #(\d+) from (.+)",
        commit_message.strip(),
        flags=re.IGNORECASE,
    )
    if pull_request_merge:
        pull_request_number, source_branch = pull_request_merge.groups()
        return (
            f"PR #{pull_request_number} merged from {source_branch} · "
            f"{commit_hash}"
        )

    return f"{commit_message} · {commit_hash}"


def _load_local_repository_events() -> list[dict[str, str]]:
    branch = _run_git_command("branch", "--show-current")
    repository_status = _run_git_command("status", "--porcelain")
    latest_commit = _run_git_command(
        "log",
        "-1",
        "--format=%h%x1f%s%x1f%an%x1f%aI",
    )

    if branch is None or repository_status is None or latest_commit is None:
        return [{"timestamp": _snapshot_timestamp(), "source": "GI", "state": "WARNING", "subject": "Local Git information unavailable"}]

    commit_parts = latest_commit.split("\x1f", maxsplit=3)
    if len(commit_parts) != 4:
        return [{"timestamp": _snapshot_timestamp(), "source": "GI", "state": "WARNING", "subject": "Local Git information unavailable"}]

    commit_hash, commit_message, commit_author, commit_timestamp = commit_parts
    snapshot = _snapshot_timestamp()
    synchronization = _get_synchronization_state()
    events = [
        {"timestamp": snapshot, "source": "GI", "state": "INFO", "subject": f"Branch: {branch or 'Not available locally'}"},
        {"timestamp": snapshot, "source": "GI", "state": "SUCCESS" if not repository_status else "WARNING", "subject": "Working tree clean" if not repository_status else "Local changes present"},
        {"timestamp": snapshot, "source": "GI", "state": "INFO", "subject": f"Synchronization: {synchronization}"},
        {"timestamp": commit_timestamp, "source": "GI", "state": "INFO", "subject": _format_git_commit_subject(commit_hash, commit_message)},
        {"timestamp": commit_timestamp, "source": "GI", "state": "INFO", "subject": f"Author: {commit_author}"},
    ]
    return sorted(events, key=lambda event: event["timestamp"], reverse=True)


def _build_github_feed(details: dict[str, Any]) -> list[dict[str, str]]:
    snapshot = details.get("last_update") or _snapshot_timestamp()
    state_mapping = {
        "Healthy": ("SUCCESS", "GitHub Healthy"),
        "Running": ("RUNNING", "GitHub"),
        "Attention required": ("FAILED", "GitHub requires attention"),
        "Not available": ("WARNING", "GitHub unavailable"),
    }
    event_state, health_message = state_mapping.get(
        details.get("state", "Not available"),
        ("WARNING", "GitHub status unavailable"),
    )
    events = [
        {"timestamp": snapshot, "source": "GH", "state": event_state, "subject": health_message}
    ]

    if details.get("reason"):
        events.append({"timestamp": snapshot, "source": "GH", "state": "WARNING", "subject": details["reason"]})
    if details.get("repository"):
        events.append({"timestamp": snapshot, "source": "GI", "state": "INFO", "subject": f"Repository: {details['repository']}"})
    if details.get("branch"):
        events.append({"timestamp": snapshot, "source": "GI", "state": "INFO", "subject": f"Branch: {details['branch']}"})

    workflow = details.get("workflow") or {}
    if workflow:
        events.append({"timestamp": snapshot, "source": "CI", "state": "INFO", "subject": f"Workflow: {workflow.get('name') or 'Unavailable'}"})
    if details.get("failed_check"):
        events.append({"timestamp": snapshot, "source": "CI", "state": "FAILED", "subject": details["failed_check"]})

    pull_request = details.get("pull_request") or {}
    if pull_request:
        pull_request_timestamp = pull_request.get("updatedAt") or snapshot
        events.append({"timestamp": pull_request_timestamp, "source": "GH", "state": "INFO", "subject": f"Pull Request #{pull_request.get('number')}: {pull_request.get('title')}"})
        if pull_request.get("reviewDecision"):
            review = str(pull_request["reviewDecision"]).replace("_", " ").title()
            events.append({"timestamp": pull_request_timestamp, "source": "GH", "state": "INFO", "subject": f"Review: {review}"})
        if pull_request.get("mergeStateStatus"):
            merge_state = str(pull_request["mergeStateStatus"]).replace("_", " ").title()
            events.append({"timestamp": pull_request_timestamp, "source": "GH", "state": "INFO", "subject": f"Merge: {merge_state}"})

    if details.get("last_update"):
        events.append({"timestamp": details["last_update"], "source": "GH", "state": "INFO", "subject": "Last GitHub update"})

    events.extend(details.get("events") or [])
    return sorted(events, key=lambda event: event["timestamp"], reverse=True)


def _render_github_feed() -> None:
    details = _load_github_status()
    _render_event_timeline(_build_github_feed(details))
    if details.get("url"):
        st.link_button("Open GitHub for investigation", details["url"])


def render_operational_detail_viewer() -> None:
    """Render compact operational details from the selected source."""
    source_key = "operational_detail_source"
    selected_source = st.session_state.get(source_key, "Git / Local Repository")
    data_source_state = "LOCAL" if selected_source == "Git / Local Repository" else "LIVE"
    render_component_header("Operational Detail Viewer", data_source_state)
    source = st.selectbox(
        "Source",
        ("Git / Local Repository", "GitHub Status"),
        label_visibility="collapsed",
        key=source_key,
    )

    if source == "Git / Local Repository":
        _render_event_timeline(_load_local_repository_events())
    elif source == "GitHub Status":
        _render_github_feed()
