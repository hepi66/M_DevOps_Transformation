from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Literal

from dashboard.lifecycle import PipelineRun
from dashboard.operational_detail_viewer import (
    get_docker_build_stage_data,
    get_ghcr_stage_data,
)

PipelineSource = Literal["DEMO", "LOCAL", "LIVE"]
PipelineData = dict[str, str | None]
PipelineDataProvider = Callable[[dict[str, Any] | None], PipelineData | None]


@dataclass(frozen=True)
class PipelineStage:
    """Describe one stage in the dashboard delivery pipeline."""

    identifier: str
    display_name: str
    platform: str
    platform_label: str
    source_classification: PipelineSource
    status: str
    description: str
    timestamp: datetime | None = None
    details: str | None = None
    detail_view: str | None = None
    data_provider: PipelineDataProvider | None = None


def get_ci_pipeline_stage_data(
    runtime_snapshot: dict[str, Any] | None = None,
) -> PipelineData:
    """Project the existing normalized workflow into the CI pipeline stage."""
    if runtime_snapshot is None:
        return {
            "source_classification": "DEMO",
            "status": "Demo",
            "timestamp": None,
            "details": "Demonstration data",
        }

    github_actions = runtime_snapshot.get("github_actions")
    if not isinstance(github_actions, dict):
        return {
            "source_classification": "LIVE",
            "status": "Unavailable",
            "timestamp": None,
            "details": runtime_snapshot.get("reason") or "Workflow data unavailable",
        }

    workflow = github_actions.get("workflow")
    if (
        github_actions.get("availability") != "available"
        or not isinstance(workflow, dict)
    ):
        return {
            "source_classification": "LIVE",
            "status": "Unavailable",
            "timestamp": None,
            "details": github_actions.get("reason") or "Workflow data unavailable",
        }

    raw_status = str(workflow.get("status") or "").lower()
    conclusion = str(workflow.get("conclusion") or "").lower()
    waiting_states = {"expected", "pending", "queued", "requested", "waiting"}
    failure_states = {
        "action_required",
        "failure",
        "startup_failure",
        "timed_out",
    }

    if raw_status in waiting_states:
        status = "Queued"
    elif raw_status == "in_progress":
        status = "Running"
    elif conclusion == "success":
        status = "Success"
    elif conclusion in failure_states:
        status = "Failed"
    elif conclusion == "cancelled":
        status = "Cancelled"
    else:
        status = "Unavailable"

    run_number = workflow.get("number")
    branch = workflow.get("headBranch")
    context = [
        f"Run #{run_number}" if run_number is not None else None,
        str(branch) if branch else None,
    ]

    return {
        "source_classification": "LIVE",
        "status": status,
        "timestamp": (
            workflow.get("updatedAt")
            or workflow.get("startedAt")
            or workflow.get("createdAt")
        ),
        "details": " · ".join(value for value in context if value) or None,
    }


PIPELINE_STAGES = (
    PipelineStage(
        identifier="code",
        display_name="Code",
        platform="Developer",
        platform_label="Dev",
        source_classification="LOCAL",
        status="Completed",
        description="A software change is created and committed.",
    ),
    PipelineStage(
        identifier="github",
        display_name="GitHub",
        platform="GitHub",
        platform_label="GitHub",
        source_classification="LIVE",
        status="Completed",
        description="The change is stored, reviewed, and versioned.",
    ),
    PipelineStage(
        identifier="ci",
        display_name="CI",
        platform="GitHub Actions",
        platform_label="Actions",
        source_classification="LIVE",
        status="Completed",
        description="Automated quality gates validate the change.",
        data_provider=get_ci_pipeline_stage_data,
    ),
    PipelineStage(
        identifier="build",
        display_name="Build",
        platform="Docker",
        platform_label="Docker",
        source_classification="LOCAL",
        status="Completed",
        description="A deployable container image is created.",
        detail_view="Docker Build",
        data_provider=get_docker_build_stage_data,
    ),
    PipelineStage(
        identifier="ghcr",
        display_name="GHCR",
        platform="GHCR",
        platform_label="GHCR",
        source_classification="LIVE",
        status="Retrieval unavailable",
        description="The immutable image is published for delivery.",
        detail_view="GHCR",
        data_provider=get_ghcr_stage_data,
    ),
    PipelineStage(
        identifier="argocd",
        display_name="Argo CD",
        platform="Argo CD",
        platform_label="Argo CD",
        source_classification="DEMO",
        status="Active",
        description="Desired state changes are detected and synchronized.",
    ),
    PipelineStage(
        identifier="kubernetes",
        display_name="Kubernetes",
        platform="Kubernetes",
        platform_label="K8s",
        source_classification="DEMO",
        status="Upcoming",
        description="The workload is rolled out and operated.",
    ),
)


def get_pipeline_stages(
    runtime_snapshot: dict[str, Any] | PipelineRun | None = None,
) -> tuple[PipelineStage, ...]:
    """Return pipeline stages with available provider data applied."""
    if isinstance(runtime_snapshot, PipelineRun):
        lifecycle_stages = {
            stage.identifier: stage
            for stage in runtime_snapshot.stages
        }
        return tuple(
            replace(
                stage,
                source_classification=(
                    lifecycle_stages[stage.identifier].source_classification
                    if stage.identifier in lifecycle_stages
                    else stage.source_classification
                ),
                status=(
                    lifecycle_stages[stage.identifier].status
                    if stage.identifier in lifecycle_stages
                    else stage.status
                ),
                timestamp=(
                    lifecycle_stages[stage.identifier].timestamp
                    if stage.identifier in lifecycle_stages
                    else stage.timestamp
                ),
                details=(
                    lifecycle_stages[stage.identifier].details
                    if stage.identifier in lifecycle_stages
                    and lifecycle_stages[stage.identifier].details
                    else stage.details
                ),
            )
            for stage in PIPELINE_STAGES
        )

    resolved_stages = []

    for stage in PIPELINE_STAGES:
        if stage.data_provider is None:
            resolved_stages.append(stage)
            continue

        try:
            provider_data = stage.data_provider(runtime_snapshot)
        except Exception:  # noqa: BLE001 - provider fallback handles all failures
            provider_data = None

        if not provider_data:
            resolved_stages.append(stage)
            continue

        timestamp = provider_data.get("timestamp")
        try:
            parsed_timestamp = (
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if timestamp
                else None
            )
        except ValueError:
            parsed_timestamp = None

        resolved_stages.append(
            replace(
                stage,
                source_classification=provider_data.get(
                    "source_classification",
                    stage.source_classification,
                ),
                status=provider_data.get("status") or stage.status,
                timestamp=parsed_timestamp,
                details=provider_data.get("details") or stage.details,
            )
        )

    return tuple(resolved_stages)
