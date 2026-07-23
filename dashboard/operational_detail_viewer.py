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
from dashboard.operational_events import (
    EventClassification,
    OperationalEvent,
    order_operational_events,
)


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


def _run_gh_process(
    *arguments: str,
) -> subprocess.CompletedProcess[str] | None:
    executable = _find_gh_executable()
    if executable is None:
        return None

    try:
        return subprocess.run(  # nosec B603 B607 - fixed read-only GitHub CLI
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


def _run_gh_command(*arguments: str) -> str | None:
    result = _run_gh_process(*arguments)
    if result is None:
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


def _run_gh_json_with_availability(
    *arguments: str,
) -> tuple[Any | None, str]:
    result = _run_gh_process(*arguments)
    if result is None:
        return None, "unavailable"
    if result.returncode != 0:
        error = result.stderr.lower()
        if "http 404" in error:
            return None, "missing"
        if (
            "http 401" in error
            or "http 403" in error
            or "authentication" in error
            or "read:packages" in error
        ):
            return None, "authentication_unavailable"
        return None, "unavailable"

    try:
        return json.loads(result.stdout), "available"
    except json.JSONDecodeError:
        return None, "unavailable"


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


def _operational_event(
    *,
    timestamp: str | None,
    source: str,
    category: str,
    status: str,
    message: str,
    order: int,
    event_id: str,
    classification: EventClassification = "lifecycle",
    detail: str | None = None,
    external_url: str | None = None,
) -> OperationalEvent:
    icon, _ = EVENT_STATE_STYLES.get(
        status.upper(),
        EVENT_STATE_STYLES["UNKNOWN"],
    )
    source_names = {
        "GI": "Git",
        "GH": "GitHub",
        "CI": "GitHub Actions",
        "DB": "Docker Build",
        "CR": "GitHub Container Registry",
    }
    if status.upper() in {"FAILED", "ATTENTION REQUIRED"}:
        classification = "failure"
    elif status.upper() == "WARNING" and classification == "lifecycle":
        classification = "warning"

    return OperationalEvent(
        timestamp=timestamp,
        source_identifier=source_names[source],
        source_abbreviation=source,
        category=category,
        status=status,
        icon=icon,
        message=message,
        classification=classification,
        detail=detail,
        external_url=external_url,
        order=order,
        event_id=event_id,
    )


def _render_event_timeline(events: list[OperationalEvent]) -> None:
    rows = [
        """
<style>
.operational-event-timeline {
    height: 380px;
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
.operational-event-timeline .event-row.lifecycle .event-subject,
.operational-event-timeline .event-row.failure .event-subject {
    font-weight: 600;
}
.operational-event-timeline .event-row.metadata {
    min-height: 28px;
    font-size: 0.76rem;
    opacity: 0.72;
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

    for event in order_operational_events(events):
        timestamp = html.escape(format_dashboard_timestamp(event.timestamp))
        subject = html.escape(event.message, quote=True)
        title = html.escape(
            " · ".join(
                value for value in (event.message, event.detail) if value
            ),
            quote=True,
        )
        state = html.escape(event.status.replace("_", " ").title())
        color = EVENT_ICON_COLORS.get(event.icon, EVENT_ICON_COLORS["?"])
        rows.append(
            f'<div class="event-row {html.escape(event.classification)}" '
            f'role="row">'
            f'<span class="event-time" role="cell">{timestamp}</span>'
            f'<span class="event-source" role="cell">'
            f'{html.escape(event.source_abbreviation)}</span>'
            f'<span class="event-state" role="cell" aria-label="{state}" '
            f'style="color: {color}">{event.icon}</span>'
            f'<span class="event-subject" role="cell" title="{title}">{subject}</span>'
            "</div>"
        )

    rows.append("</div>")
    st.html("\n".join(rows))


def _build_operational_events(
    runs: list[dict[str, Any]],
) -> list[OperationalEvent]:
    events = []

    for run_index, run in enumerate(runs):
        workflow_name = run.get("name") or "Workflow"
        run_id = str(run.get("databaseId") or run_index)
        if run.get("startedAt"):
            events.append(
                _operational_event(
                    timestamp=run["startedAt"],
                    source="CI",
                    category="github",
                    status="RUNNING",
                    message=f"{workflow_name} started",
                    detail=_execution_detail(run),
                    order=20,
                    event_id=f"workflow:{run_id}:started",
                    external_url=run.get("url"),
                )
            )

        if run.get("status") == "completed" and run.get("updatedAt"):
            state = _workflow_event_state(run.get("conclusion"))
            conclusion = str(run.get("conclusion") or "").replace("_", " ")
            completion = {
                "success": "completed successfully",
                "failure": "failed",
                "timed out": "timed out",
                "cancelled": "cancelled",
                "skipped": "skipped",
            }.get(conclusion, f"completed {conclusion}".strip())
            events.append(
                _operational_event(
                    timestamp=run["updatedAt"],
                    source="CI",
                    category="github",
                    status=state,
                    message=f"{workflow_name} {completion}",
                    detail=_execution_detail(run),
                    order=10,
                    event_id=f"workflow:{run_id}:completed",
                    external_url=run.get("url"),
                )
            )
        elif run.get("createdAt") and not run.get("startedAt"):
            events.append(
                _operational_event(
                    timestamp=run["createdAt"],
                    source="CI",
                    category="github",
                    status="QUEUED",
                    message=f"{workflow_name} queued",
                    detail=_execution_detail(run),
                    order=30,
                    event_id=f"workflow:{run_id}:queued",
                    external_url=run.get("url"),
                )
            )

    return order_operational_events(events)[:10]


def _load_github_actions_details(
    runs: list[dict[str, Any]],
    workflow_name: str,
) -> dict[str, Any]:
    workflow = next(
        (run for run in runs if run.get("name") == workflow_name),
        None,
    )
    if not workflow:
        return {
            "availability": "missing",
            "reason": f"No {workflow_name} workflow execution was found.",
        }
    if not workflow.get("databaseId"):
        return {
            "availability": "incomplete",
            "workflow": workflow,
            "reason": "The workflow run identifier is unavailable.",
        }

    run_details = _run_gh_json(
        "run",
        "view",
        str(workflow["databaseId"]),
        "--json",
        "jobs",
    )
    jobs = run_details.get("jobs") if isinstance(run_details, dict) else None
    if not isinstance(jobs, list):
        return {
            "availability": "unavailable",
            "workflow": workflow,
            "reason": "GitHub Actions job information could not be retrieved.",
        }

    normalized_jobs = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        normalized_job = dict(job)
        normalized_job["steps"] = [
            dict(step)
            for step in (job.get("steps") or [])
            if isinstance(step, dict)
        ]
        normalized_jobs.append(normalized_job)

    return {
        "availability": "available",
        "workflow": workflow,
        "jobs": normalized_jobs,
    }


def _project_docker_build(
    github_actions: dict[str, Any],
    *,
    job_name: str,
    step_name: str,
) -> dict[str, Any]:
    availability = github_actions.get("availability")
    if availability != "available":
        return {
            key: value
            for key, value in github_actions.items()
            if key in {"availability", "workflow", "reason"}
        }

    workflow = github_actions.get("workflow")
    jobs = github_actions.get("jobs") or []
    job = next(
        (item for item in jobs if item.get("name") == job_name),
        None,
    )
    if not job:
        return {
            "availability": "unrecognized",
            "workflow": workflow,
            "reason": f"The expected {job_name} job was not found.",
        }

    steps = job.get("steps") or []
    step = next(
        (step for step in steps if step.get("name") == step_name),
        None,
    )
    if not step:
        return {
            "availability": "unrecognized",
            "workflow": workflow,
            "job": job,
            "reason": f"The expected {step_name} step was not found.",
        }

    return {
        "availability": "available",
        "workflow": workflow,
        "job": job,
        "step": step,
    }


def _load_ghcr_package(repository: dict[str, Any]) -> dict[str, Any]:
    owner = (repository.get("owner") or {}).get("login")
    package_name = str(repository.get("name") or "").lower()
    if not owner or not package_name:
        return {
            "availability": "unavailable",
            "reason": "GHCR package coordinates could not be resolved.",
        }

    package_endpoint = f"/users/{owner}/packages/container/{package_name}"
    package, package_availability = _run_gh_json_with_availability(
        "api",
        package_endpoint,
    )
    if not isinstance(package, dict):
        return {
            "availability": package_availability,
            "package_name": package_name,
            "image_name": f"ghcr.io/{owner}/{package_name}",
            "reason": (
                "The GHCR package does not exist."
                if package_availability == "missing"
                else "GHCR authentication is unavailable."
                if package_availability == "authentication_unavailable"
                else "The GHCR package could not be retrieved."
            ),
        }

    versions, versions_availability = _run_gh_json_with_availability(
        "api",
        f"{package_endpoint}/versions?per_page=1",
    )
    if versions_availability != "available":
        return {
            "availability": versions_availability,
            "package_name": package.get("name") or package_name,
            "image_name": f"ghcr.io/{owner}/{package_name}",
            "package_url": package.get("html_url"),
            "visibility": package.get("visibility"),
            "reason": (
                "GHCR authentication is unavailable."
                if versions_availability == "authentication_unavailable"
                else "GHCR package versions could not be retrieved."
            ),
        }
    if not isinstance(versions, list) or not versions:
        return {
            "availability": "missing",
            "package_name": package.get("name") or package_name,
            "image_name": f"ghcr.io/{owner}/{package_name}",
            "package_url": package.get("html_url"),
            "visibility": package.get("visibility"),
            "reason": "No published GHCR image version was found.",
        }

    version = versions[0]
    container_metadata = (version.get("metadata") or {}).get("container") or {}
    tags = container_metadata.get("tags") or []
    latest_tag = "latest" if "latest" in tags else (tags[0] if tags else None)
    return {
        "availability": "available",
        "package_name": package.get("name") or package_name,
        "image_name": f"ghcr.io/{owner}/{package_name}",
        "latest_tag": latest_tag,
        "published_at": version.get("updated_at") or version.get("created_at"),
        "digest": version.get("name"),
        "package_url": (
            package.get("html_url")
            or version.get("package_html_url")
        ),
        "visibility": package.get("visibility"),
    }


@st.cache_data(ttl=60, show_spinner=False)
def _load_github_status() -> dict[str, Any]:
    remote = _run_git_command("remote", "get-url", "origin")
    if not remote or "github.com" not in remote.lower():
        return {"state": "Not available", "reason": "GitHub remote is unavailable."}

    if _run_gh_command("auth", "status") is None:
        return {
            "state": "Not available",
            "reason": "GitHub CLI is unavailable or not authenticated.",
            "ghcr": {
                "availability": "authentication_unavailable",
                "reason": "GitHub authentication is unavailable.",
            },
        }

    repository = _run_gh_json(
        "repo",
        "view",
        "--json",
        "name,nameWithOwner,owner,url",
    )
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
        "databaseId,number,name,displayTitle,status,conclusion,"
        "createdAt,startedAt,updatedAt,url,headBranch,headSha",
    )
    workflow = runs[0] if isinstance(runs, list) and runs else None
    github_actions = (
        _load_github_actions_details(
            runs,
            workflow_name="CI Pipeline",
        )
        if isinstance(runs, list)
        else {
            "availability": "unavailable",
            "reason": "GitHub Actions workflow executions could not be retrieved.",
        }
    )
    docker_build = _project_docker_build(
        github_actions,
        job_name="build",
        step_name="Build and push",
    )
    ghcr = _load_ghcr_package(repository)

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
        "repository_url": repository.get("url"),
        "branch": branch,
        "workflow": workflow,
        "github_actions": github_actions,
        "docker_build": docker_build,
        "ghcr": ghcr,
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
        "refreshed_at": datetime.now().astimezone().isoformat(),
    }


def load_dashboard_snapshot() -> dict[str, Any]:
    """Return the authoritative cached runtime snapshot for one rerun."""
    return _load_github_status()


def clear_dashboard_snapshot() -> None:
    """Invalidate the cached runtime snapshot."""
    _load_github_status.clear()


def get_ghcr_data(
    runtime_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return normalized GHCR data from the cached GitHub snapshot."""
    details = (
        runtime_snapshot
        if runtime_snapshot is not None
        else load_dashboard_snapshot()
    )
    ghcr = details.get("ghcr")
    if isinstance(ghcr, dict):
        return ghcr
    return {
        "availability": "unavailable",
        "reason": details.get("reason") or "GHCR retrieval is unavailable.",
    }


def get_ghcr_stage_data(
    runtime_snapshot: dict[str, Any] | None = None,
) -> dict[str, str | None]:
    """Return the live GHCR state for the centralized pipeline model."""
    details = get_ghcr_data(runtime_snapshot)
    availability = details.get("availability")
    status = {
        "available": "Image published",
        "missing": "Image unavailable",
        "unavailable": "Retrieval unavailable",
        "authentication_unavailable": "Authentication unavailable",
    }.get(availability, "Retrieval unavailable")

    return {
        "source_classification": "LIVE",
        "status": status,
        "timestamp": details.get("published_at"),
        "details": details.get("image_name") or details.get("reason"),
    }


def get_docker_build_stage_data(
    runtime_snapshot: dict[str, Any] | None = None,
) -> dict[str, str] | None:
    """Return the latest Docker build state from the existing GitHub data."""
    snapshot = (
        runtime_snapshot
        if runtime_snapshot is not None
        else load_dashboard_snapshot()
    )
    details = snapshot.get("docker_build")
    if not isinstance(details, dict) or details.get("availability") != "available":
        return None

    job = details.get("job")
    step = details.get("step")
    if not isinstance(job, dict) or not isinstance(step, dict):
        return None

    state = _classify_docker_build(job, step)
    status = {
        "Attention required": "Failed",
        "Healthy": "Completed",
        "Running": "Active",
    }.get(state)
    if status is None:
        return None

    return {
        "source_classification": "LIVE",
        "status": status,
        "timestamp": (
            step.get("completedAt")
            or step.get("startedAt")
            or job.get("completedAt")
            or job.get("startedAt")
        ),
        "details": step.get("name") or "Build and push",
    }


def _classify_docker_build(
    job: dict[str, Any],
    step: dict[str, Any],
) -> str:
    states = [
        _classify_github_status(item.get("status"), item.get("conclusion"))
        for item in (job, step)
    ]
    if "Attention required" in states:
        return "Attention required"
    if "Running" in states:
        return "Running"
    if all(state == "Healthy" for state in states):
        return "Healthy"
    return "Not available"


def _execution_detail(
    workflow: dict[str, Any],
    *,
    job: dict[str, Any] | None = None,
    step: dict[str, Any] | None = None,
) -> str:
    run_identifier = workflow.get("number") or workflow.get("databaseId")
    values = [
        f"Workflow: {workflow.get('name') or 'Unknown'}",
        f"Run: {run_identifier or 'Unknown'}",
    ]
    if workflow.get("headBranch"):
        values.append(f"Branch: {workflow['headBranch']}")
    if workflow.get("headSha"):
        values.append(f"Commit: {workflow['headSha'][:7]}")
    if job and job.get("name"):
        values.append(f"Job: {job['name']}")
    if step and step.get("name"):
        values.append(f"Step: {step['name']}")
    return " · ".join(values)


def _step_progress_event(
    *,
    workflow: dict[str, Any],
    job: dict[str, Any],
    step: dict[str, Any],
    source: str,
    category: str,
    event_prefix: str,
    success_message: str,
    failure_message: str,
    running_message: str,
    order: int,
) -> OperationalEvent | None:
    conclusion = str(step.get("conclusion") or "").lower()
    status = str(step.get("status") or "").lower()
    detail = _execution_detail(workflow, job=job, step=step)

    if conclusion:
        state = _workflow_event_state(conclusion)
        message = (
            success_message
            if conclusion == "success"
            else failure_message
        )
        return _operational_event(
            timestamp=step.get("completedAt") or step.get("startedAt"),
            source=source,
            category=category,
            status=state,
            message=message,
            detail=detail,
            order=order,
            event_id=f"{event_prefix}:completed",
            external_url=workflow.get("url"),
        )

    if status in {"in_progress", "pending", "queued", "waiting"}:
        return _operational_event(
            timestamp=step.get("startedAt"),
            source=source,
            category=category,
            status="RUNNING" if status == "in_progress" else "QUEUED",
            message=running_message,
            detail=detail,
            order=order,
            event_id=f"{event_prefix}:running",
            external_url=workflow.get("url"),
        )

    return None


def _build_quality_gate_feed(
    snapshot: dict[str, Any],
) -> list[OperationalEvent]:
    github_actions = snapshot.get("github_actions") or {}
    if github_actions.get("availability") != "available":
        return []

    workflow = github_actions.get("workflow") or {}
    jobs = github_actions.get("jobs") or []
    run_id = str(workflow.get("databaseId") or "latest")
    events = []
    job_definitions = {
        "linting": {
            "start": "Linting started",
            "success": "Linting completed successfully",
            "failure": "Linting failed",
            "steps": {
                "Run Ruff (Linting)": (
                    "Ruff completed successfully",
                    "Ruff failed",
                    "Ruff is running",
                ),
                "Run Bandit (Security)": (
                    "Security scan completed successfully",
                    "Security scan failed",
                    "Security scan is running",
                ),
            },
        },
        "test": {
            "start": "Tests started",
            "success": None,
            "failure": "Testing job failed",
            "steps": {
                "Run Tests": (
                    "Tests completed successfully",
                    "Tests failed",
                    "Tests are running",
                ),
            },
        },
    }

    for job_index, job in enumerate(jobs):
        definition = job_definitions.get(job.get("name"))
        if not definition:
            continue

        job_name = str(job.get("name"))
        detail = _execution_detail(workflow, job=job)
        if job.get("startedAt"):
            events.append(
                _operational_event(
                    timestamp=job["startedAt"],
                    source="CI",
                    category="github",
                    status="RUNNING",
                    message=str(definition["start"]),
                    detail=detail,
                    order=100 + job_index * 20,
                    event_id=f"quality:{run_id}:{job_name}:started",
                    external_url=workflow.get("url"),
                )
            )

        meaningful_steps = definition["steps"]
        for step_index, step in enumerate(job.get("steps") or []):
            messages = meaningful_steps.get(step.get("name"))
            if messages:
                event = _step_progress_event(
                    workflow=workflow,
                    job=job,
                    step=step,
                    source="CI",
                    category="github",
                    event_prefix=(
                        f"quality:{run_id}:{job_name}:{step.get('name')}"
                    ),
                    success_message=messages[0],
                    failure_message=messages[1],
                    running_message=messages[2],
                    order=101 + job_index * 20 + step_index,
                )
            else:
                event = _diagnostic_setup_step_event(
                    workflow=workflow,
                    job=job,
                    step=step,
                    source="CI",
                    category="github",
                    event_prefix=f"quality:{run_id}:{job_name}:setup",
                    order=101 + job_index * 20 + step_index,
                )
            if event:
                events.append(event)

        conclusion = str(job.get("conclusion") or "").lower()
        completion_message = (
            definition["success"]
            if conclusion == "success"
            else definition["failure"]
        )
        if job.get("completedAt") and completion_message:
            events.append(
                _operational_event(
                    timestamp=job["completedAt"],
                    source="CI",
                    category="github",
                    status=_workflow_event_state(conclusion),
                    message=str(completion_message),
                    detail=detail,
                    order=119 + job_index * 20,
                    event_id=f"quality:{run_id}:{job_name}:completed",
                    external_url=workflow.get("url"),
                )
            )

    return order_operational_events(events)


def _diagnostic_setup_step_event(
    *,
    workflow: dict[str, Any],
    job: dict[str, Any],
    step: dict[str, Any],
    source: str,
    category: str,
    event_prefix: str,
    order: int,
) -> OperationalEvent | None:
    conclusion = str(step.get("conclusion") or "").lower()
    status = str(step.get("status") or "").lower()
    if conclusion not in {
        "action_required",
        "cancelled",
        "failure",
        "startup_failure",
        "timed_out",
    } and status not in {"in_progress", "pending", "queued", "waiting"}:
        return None

    step_name = step.get("name") or "Setup step"
    is_running = not conclusion
    return _operational_event(
        timestamp=(
            step.get("startedAt")
            if is_running
            else step.get("completedAt") or step.get("startedAt")
        ),
        source=source,
        category=category,
        status=(
            "RUNNING"
            if status == "in_progress"
            else "QUEUED"
            if is_running
            else _workflow_event_state(conclusion)
        ),
        message=(
            f"{step_name} is running"
            if is_running
            else f"{step_name} failed"
        ),
        detail=_execution_detail(workflow, job=job, step=step),
        order=order,
        event_id=f"{event_prefix}:{step_name}:diagnostic",
        external_url=workflow.get("url"),
    )


def _build_docker_build_feed(
    snapshot: dict[str, Any],
) -> list[OperationalEvent]:
    details = snapshot.get("docker_build")

    if not isinstance(details, dict):
        return [
            _operational_event(
                timestamp=None,
                source="DB",
                category="docker-build",
                status="WARNING",
                message="Docker Build live data unavailable",
                classification="warning",
                detail=snapshot.get("reason"),
                order=90,
                event_id="docker-build:unavailable",
            )
        ]

    availability = details.get("availability")
    if availability != "available":
        messages = {
            "missing": "No Docker Build workflow execution found",
            "unavailable": "GitHub Actions workflow data unavailable",
            "incomplete": "Docker Build workflow metadata incomplete",
            "unrecognized": details.get("reason")
            or "Docker Build workflow structure unrecognized",
        }
        return [
            _operational_event(
                timestamp=None,
                source="DB",
                category="docker-build",
                status="WARNING",
                message=messages.get(
                    availability,
                    "Docker Build details unavailable",
                ),
                classification="warning",
                detail=details.get("reason"),
                order=90,
                event_id=f"docker-build:{availability or 'unknown'}",
            )
        ]

    workflow = details.get("workflow") or {}
    job = details.get("job") or {}
    step = details.get("step") or {}
    run_id = str(workflow.get("databaseId") or "latest")
    events = []

    if workflow.get("createdAt"):
        workflow_state = (
            "QUEUED"
            if str(workflow.get("status") or "").lower() == "queued"
            else "INFO"
        )
        workflow_message = (
            "CI Pipeline queued"
            if workflow_state == "QUEUED"
            else "CI Pipeline execution identified"
        )
        events.append(
            _operational_event(
                timestamp=workflow["createdAt"],
                source="CI",
                category="docker-build",
                status=workflow_state,
                message=workflow_message,
                classification=(
                    "lifecycle"
                    if workflow_state == "QUEUED"
                    else "information"
                ),
                order=20,
                event_id=(
                    f"workflow:{run_id}:queued"
                    if workflow_state == "QUEUED"
                    else f"workflow:{run_id}:identified"
                ),
                external_url=workflow.get("url"),
            )
        )
    if workflow.get("startedAt"):
        events.append(
            _operational_event(
                timestamp=workflow["startedAt"],
                source="CI",
                category="docker-build",
                status="RUNNING",
                message="CI Pipeline started",
                order=21,
                event_id=f"workflow:{run_id}:started",
                external_url=workflow.get("url"),
            )
        )
    if job.get("startedAt"):
        events.append(
            _operational_event(
                timestamp=job["startedAt"],
                source="DB",
                category="docker-build",
                status="RUNNING",
                message="Docker Build started",
                order=30,
                event_id=f"docker-build:{run_id}:job:started",
                external_url=workflow.get("url"),
            )
        )
    if step.get("startedAt"):
        events.append(
            _operational_event(
                timestamp=step["startedAt"],
                source="DB",
                category="docker-build",
                status="RUNNING",
                message="Build and push started",
                order=40,
                event_id=f"docker-build:{run_id}:step:started",
                external_url=workflow.get("url"),
            )
        )

    for step_index, build_step in enumerate(job.get("steps") or []):
        step_name = build_step.get("name")
        if step_name == "Login to GitHub Container Registry":
            registry_event = _step_progress_event(
                workflow=workflow,
                job=job,
                step=build_step,
                source="DB",
                category="docker-build",
                event_prefix=f"docker-build:{run_id}:registry-login",
                success_message="Registry login completed successfully",
                failure_message="Registry login failed",
                running_message="Registry login is running",
                order=35,
            )
            if registry_event:
                events.append(registry_event)
        elif step_name != "Build and push":
            setup_event = _diagnostic_setup_step_event(
                workflow=workflow,
                job=job,
                step=build_step,
                source="DB",
                category="docker-build",
                event_prefix=f"docker-build:{run_id}:setup",
                order=31 + step_index,
            )
            if setup_event:
                events.append(setup_event)

    job_conclusion = str(job.get("conclusion") or "").lower()
    if job.get("completedAt"):
        job_status = _workflow_event_state(job_conclusion)
        job_message = {
            "success": "Docker Build completed successfully",
            "failure": "Docker Build job failed",
            "timed_out": "Docker Build job timed out",
            "cancelled": "Docker Build job cancelled",
            "skipped": "Docker Build job skipped",
        }.get(job_conclusion, "Docker Build job completed")
        events.append(
            _operational_event(
                timestamp=job["completedAt"],
                source="DB",
                category="docker-build",
                status=job_status,
                message=job_message,
                order=31,
                event_id=f"docker-build:{run_id}:job:completed",
                external_url=workflow.get("url"),
            )
        )

    step_conclusion = str(step.get("conclusion") or "").lower()
    if step.get("completedAt"):
        step_status = _workflow_event_state(step_conclusion)
        step_message = {
            "success": "Build and push completed successfully",
            "failure": "Build and push step failed",
            "timed_out": "Build and push step timed out",
            "cancelled": "Build and push step cancelled",
            "skipped": "Build and push step skipped",
        }.get(step_conclusion, "Build and push completed")
        events.append(
            _operational_event(
                timestamp=step["completedAt"],
                source="DB",
                category="docker-build",
                status=step_status,
                message=step_message,
                order=41,
                event_id=f"docker-build:{run_id}:step:completed",
                external_url=workflow.get("url"),
            )
        )

    if workflow.get("status") == "completed" and workflow.get("updatedAt"):
        conclusion = str(workflow.get("conclusion") or "").lower()
        message = {
            "success": "CI Pipeline completed successfully",
            "failure": "CI Pipeline failed",
            "timed_out": "CI Pipeline timed out",
            "cancelled": "CI Pipeline cancelled",
            "skipped": "CI Pipeline skipped",
        }.get(conclusion, "CI Pipeline completed")
        events.append(
            _operational_event(
                timestamp=workflow["updatedAt"],
                source="CI",
                category="docker-build",
                status=_workflow_event_state(conclusion),
                message=message,
                order=10,
                event_id=f"workflow:{run_id}:completed",
                external_url=workflow.get("url"),
            )
        )

    if not events:
        events.append(
            _operational_event(
                timestamp=None,
                source="DB",
                category="docker-build",
                status="WARNING",
                message="Docker Build workflow data incomplete",
                classification="warning",
                order=90,
                event_id=f"docker-build:{run_id}:incomplete",
            )
        )

    return order_operational_events(events)


def _format_git_commit_subject(commit_hash: str, commit_message: str) -> str:
    pull_request_merge = re.fullmatch(
        r"Merge pull request #(\d+) from (.+)",
        commit_message.strip(),
        flags=re.IGNORECASE,
    )
    if pull_request_merge:
        pull_request_number, source_branch = pull_request_merge.groups()
        return (
            f"Pull request #{pull_request_number} merged from "
            f"{source_branch} · {commit_hash}"
        )

    return f"Commit {commit_hash}: {commit_message}"


def _load_local_repository_events() -> list[OperationalEvent]:
    branch = _run_git_command("branch", "--show-current")
    repository_status = _run_git_command("status", "--porcelain")
    latest_commit = _run_git_command(
        "log",
        "-1",
        "--format=%h%x1f%s%x1f%an%x1f%aI",
    )

    if branch is None or repository_status is None or latest_commit is None:
        return [
            _operational_event(
                timestamp=None,
                source="GI",
                category="github",
                status="WARNING",
                message="Local Git information unavailable",
                classification="warning",
                order=90,
                event_id="git:unavailable",
            )
        ]

    commit_parts = latest_commit.split("\x1f", maxsplit=3)
    if len(commit_parts) != 4:
        return [
            _operational_event(
                timestamp=None,
                source="GI",
                category="github",
                status="WARNING",
                message="Local Git information unavailable",
                classification="warning",
                order=90,
                event_id="git:unavailable",
            )
        ]

    commit_hash, commit_message, commit_author, commit_timestamp = commit_parts
    synchronization = _get_synchronization_state()
    events = [
        _operational_event(
            timestamp=None,
            source="GI",
            category="github",
            status="INFO",
            message=f"Local branch {branch or 'unavailable'} inspected",
            classification="metadata",
            order=40,
            event_id="git:branch",
        ),
        _operational_event(
            timestamp=None,
            source="GI",
            category="github",
            status="SUCCESS" if not repository_status else "WARNING",
            message="Working tree clean" if not repository_status else "Local changes present",
            classification="status",
            order=41,
            event_id="git:working-tree",
        ),
        _operational_event(
            timestamp=None,
            source="GI",
            category="github",
            status="INFO",
            message=f"Repository synchronization: {synchronization}",
            classification="metadata",
            order=42,
            event_id="git:synchronization",
        ),
        _operational_event(
            timestamp=commit_timestamp,
            source="GI",
            category="github",
            status="INFO",
            message=_format_git_commit_subject(commit_hash, commit_message),
            detail=f"Author: {commit_author}",
            order=43,
            event_id=f"git:commit:{commit_hash}",
        ),
    ]
    return order_operational_events(events)


def _build_github_feed(details: dict[str, Any]) -> list[OperationalEvent]:
    snapshot = details.get("last_update")
    state_mapping = {
        "Healthy": ("SUCCESS", "GitHub repository healthy"),
        "Running": ("RUNNING", "GitHub"),
        "Attention required": ("FAILED", "GitHub requires attention"),
        "Not available": ("WARNING", "GitHub unavailable"),
    }
    event_state, health_message = state_mapping.get(
        details.get("state", "Not available"),
        ("WARNING", "GitHub status unavailable"),
    )
    events = [
        _operational_event(
            timestamp=snapshot,
            source="GH",
            category="github",
            status=event_state,
            message=health_message,
            classification="status",
            detail=" · ".join(
                value
                for value in (
                    (
                        f"Repository: {details['repository']}"
                        if details.get("repository")
                        else None
                    ),
                    (
                        f"Branch: {details['branch']}"
                        if details.get("branch")
                        else None
                    ),
                )
                if value
            )
            or None,
            order=1,
            event_id="github:health",
            external_url=details.get("url"),
        )
    ]

    if details.get("reason"):
        events.append(
            _operational_event(
                timestamp=None,
                source="GH",
                category="github",
                status="WARNING",
                message=details["reason"],
                classification="warning",
                order=2,
                event_id="github:reason",
            )
        )
    if details.get("branch"):
        events.append(
            _operational_event(
                timestamp=snapshot,
                source="GI",
                category="github",
                status="INFO",
                message=f"Pipeline branch resolved: {details['branch']}",
                classification="metadata",
                order=3,
                event_id="github:branch",
            )
        )
    workflow = details.get("workflow") or {}
    if workflow:
        workflow_id = workflow.get("databaseId") or "latest"
        events.append(
            _operational_event(
                timestamp=workflow.get("createdAt") or snapshot,
                source="CI",
                category="github",
                status="INFO",
                message=(
                    f"{workflow.get('name') or 'Workflow'} execution identified"
                ),
                classification="information",
                order=5,
                event_id=f"workflow:{workflow_id}:identified",
                external_url=workflow.get("url"),
            )
        )
    if details.get("failed_check"):
        events.append(
            _operational_event(
                timestamp=snapshot,
                source="CI",
                category="github",
                status="FAILED",
                message=details["failed_check"],
                classification="failure",
                order=6,
                event_id="github:failed-check",
            )
        )

    pull_request = details.get("pull_request") or {}
    if pull_request:
        pull_request_timestamp = pull_request.get("updatedAt") or snapshot
        events.append(
            _operational_event(
                timestamp=pull_request_timestamp,
                source="GH",
                category="github",
                status="INFO",
                message=(
                    f"Pull request #{pull_request.get('number')} open: "
                    f"{pull_request.get('title')}"
                ),
                classification="status",
                order=7,
                event_id=f"github:pr:{pull_request.get('number')}",
                external_url=pull_request.get("url"),
            )
        )
        if pull_request.get("reviewDecision"):
            review = str(pull_request["reviewDecision"]).replace("_", " ").title()
            events.append(
                _operational_event(
                    timestamp=pull_request_timestamp,
                    source="GH",
                    category="github",
                    status="INFO",
                    message=(
                        f"Pull request #{pull_request.get('number')} "
                        f"review: {review}"
                    ),
                    classification="status",
                    order=8,
                    event_id=f"github:pr:{pull_request.get('number')}:review",
                )
            )
        if pull_request.get("mergeStateStatus"):
            merge_state = str(pull_request["mergeStateStatus"]).replace("_", " ").title()
            events.append(
                _operational_event(
                    timestamp=pull_request_timestamp,
                    source="GH",
                    category="github",
                    status="INFO",
                    message=(
                        f"Pull request #{pull_request.get('number')} "
                        f"merge state: {merge_state}"
                    ),
                    classification="status",
                    order=9,
                    event_id=f"github:pr:{pull_request.get('number')}:merge",
                )
            )

    events.extend(details.get("events") or [])
    events.extend(_build_quality_gate_feed(details))
    return order_operational_events(events)


def _build_ghcr_feed(snapshot: dict[str, Any]) -> list[OperationalEvent]:
    details = snapshot.get("ghcr") or {}
    availability = details.get("availability")
    if availability == "available":
        image_name = details.get("image_name") or "GHCR image"
        latest_tag = details.get("latest_tag")
        image_reference = (
            f"{image_name}:{latest_tag}" if latest_tag else image_name
        )
        detail_values = [
            f"Image: {image_reference}",
            (
                f"Digest: {details['digest']}"
                if details.get("digest")
                else None
            ),
            (
                f"Visibility: {details['visibility']}"
                if details.get("visibility")
                else None
            ),
        ]
        return [
            _operational_event(
                timestamp=details.get("published_at"),
                source="CR",
                category="ghcr",
                status="SUCCESS",
                message="GHCR image published",
                detail=" Â· ".join(
                    value for value in detail_values if value
                ),
                order=50,
                event_id=(
                    f"ghcr:{details.get('package_name')}:"
                    f"{details.get('digest') or details.get('published_at')}"
                ),
                external_url=details.get("package_url"),
            )
        ]

    messages = {
        "missing": "GHCR image unavailable",
        "authentication_unavailable": "GHCR authentication unavailable",
        "unavailable": "GHCR retrieval unavailable",
    }
    return [
        _operational_event(
            timestamp=None,
            source="CR",
            category="ghcr",
            status="WARNING",
            message=messages.get(
                availability,
                "GHCR retrieval unavailable",
            ),
            classification="warning",
            detail=details.get("reason"),
            order=90,
            event_id=f"ghcr:{availability or 'unavailable'}",
            external_url=details.get("package_url"),
        )
    ]


def _render_context_action(
    details: dict[str, Any],
    *,
    source: str,
) -> None:
    workflow = (details.get("docker_build") or {}).get("workflow") or {}
    latest_workflow = details.get("workflow") or workflow
    actions = {
        "All": (
            "Open Latest Pipeline Run",
            latest_workflow.get("url"),
        ),
        "GitHub Status": (
            "Open Repository",
            details.get("repository_url"),
        ),
        "Docker Build": (
            "Open GitHub Actions Run",
            workflow.get("url"),
        ),
        "GHCR": (
            "Open GHCR Package",
            (details.get("ghcr") or {}).get("package_url"),
        ),
    }
    label, url = actions.get(source, (None, None))
    if not url:
        label = "Open GitHub for investigation"
        url = details.get("url")

    if label and url:
        st.link_button(label, url)


def _render_refresh_time(details: dict[str, Any]) -> None:
    refreshed_at = details.get("refreshed_at")
    if refreshed_at:
        st.caption(
            f"Last refreshed: {format_dashboard_timestamp(refreshed_at)}"
        )
    else:
        st.caption("Last refreshed: Not available")


def _render_operational_context(details: dict[str, Any]) -> None:
    repository = details.get("repository") or "Not available"
    state = details.get("state") or "Not available"
    branch = details.get("branch") or "Not available"
    st.caption(
        f"Repository · {repository} · {state}  |  Branch · {branch}"
    )


def _timeline_presentation_events(
    events: list[OperationalEvent],
) -> list[OperationalEvent]:
    context_event_ids = {"github:health", "github:branch"}
    return [
        event for event in events if event.event_id not in context_event_ids
    ]


def _render_operational_timeline(events: list[OperationalEvent]) -> None:
    _render_event_timeline(_timeline_presentation_events(events))


def render_operational_detail_viewer(
    runtime_snapshot: dict[str, Any] | None = None,
) -> None:
    """Render compact operational details from the selected source."""
    source_key = "operational_detail_source"
    selected_source = st.session_state.get(source_key, "All")
    data_source_state = "LOCAL" if selected_source == "Git / Local Repository" else "LIVE"
    render_component_header("Operational Detail Viewer", data_source_state)
    source = st.selectbox(
        "Source",
        (
            "All",
            "Git / Local Repository",
            "GitHub Status",
            "Docker Build",
            "GHCR",
        ),
        label_visibility="collapsed",
        key=source_key,
    )

    if source == "Git / Local Repository":
        _render_operational_timeline(_load_local_repository_events())
        return

    details = (
        runtime_snapshot
        if runtime_snapshot is not None
        else load_dashboard_snapshot()
    )
    _render_refresh_time(details)
    _render_operational_context(details)
    github_events = _build_github_feed(details)
    docker_build_events = _build_docker_build_feed(details)
    ghcr_events = _build_ghcr_feed(details)

    if source == "All":
        events = [
            *_load_local_repository_events(),
            *github_events,
            *docker_build_events,
            *ghcr_events,
        ]
        _render_operational_timeline(events)
        _render_context_action(details, source=source)
    elif source == "GitHub Status":
        _render_operational_timeline(github_events)
        _render_context_action(details, source=source)
    elif source == "Docker Build":
        _render_operational_timeline(docker_build_events)
        _render_context_action(details, source=source)
    elif source == "GHCR":
        _render_operational_timeline(ghcr_events)
        _render_context_action(details, source=source)
