from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Literal

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
    runtime_snapshot: dict[str, Any] | None = None,
) -> tuple[PipelineStage, ...]:
    """Return pipeline stages with available provider data applied."""
    resolved_stages = []

    for stage in PIPELINE_STAGES:
        if stage.data_provider is None:
            resolved_stages.append(stage)
            continue

        try:
            provider_data = stage.data_provider(runtime_snapshot)
        except Exception:  # Keep the static stage available if retrieval fails.
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
