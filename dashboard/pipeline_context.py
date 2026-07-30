from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dashboard.lifecycle import PipelineRun
    from dashboard.operational_events import OperationalEvent

# Authoritative operational source vocabulary. Its insertion order is the
# deterministic lifecycle order used by the Viewer and footer.
OPERATIONAL_SOURCES = {
    "GI": {
        "stage": "Code",
        "identifier": "code",
        "label": "Git",
        "color": "#F7E263",
    },
    "GH": {
        "stage": "GitHub",
        "identifier": "github",
        "label": "GitHub",
        "color": "#8B5CF6",
    },
    "CI": {
        "stage": "CI",
        "identifier": "ci",
        "label": "CI/CD",
        "color": "#D946EF",
    },
    "DB": {
        "stage": "Build",
        "identifier": "build",
        "label": "Docker Build",
        "color": "#06B6D4",
    },
    "CR": {
        "stage": "GHCR",
        "identifier": "ghcr",
        "label": "GHCR",
        "color": "#F59E0B",
    },
    "CD": {
        "stage": "Argo CD",
        "identifier": "argocd",
        "label": "Argo CD",
        "color": "#F97360",
    },
    "K8": {
        "stage": "Kubernetes",
        "identifier": "kubernetes",
        "label": "Kubernetes",
        "color": "#73B0E7",
    },
}

PIPELINE_STAGE_FILTERS = (
    "All",
    "Code",
    "GitHub",
    "CI",
    "Build",
    "GHCR",
    "Argo CD",
    "Kubernetes",
)
PIPELINE_STAGE_IDENTIFIERS = {
    "Code": "code",
    "GitHub": "github",
    "CI": "ci",
    "Build": "build",
    "GHCR": "ghcr",
    "Argo CD": "argocd",
    "Kubernetes": "kubernetes",
}
PIPELINE_STAGE_CONTEXT_COLORS = {
    definition["identifier"]: definition["color"]
    for definition in OPERATIONAL_SOURCES.values()
}
LEGACY_FILTER_STAGES = {
    "Git / Local Repository": "Code",
    "GitHub Status": "GitHub",
    "Docker Build": "Build",
}
EVENT_SOURCE_STAGES = {
    source: definition["stage"]
    for source, definition in OPERATIONAL_SOURCES.items()
}
PIPELINE_STAGE_SOURCES = {
    stage: source for source, stage in EVENT_SOURCE_STAGES.items()
}
PIPELINE_IDENTIFIER_STAGES = {
    identifier: stage
    for stage, identifier in PIPELINE_STAGE_IDENTIFIERS.items()
}
PIPELINE_SELECTION_OVERRIDE_KEY = "pipeline_selection_manual"
PIPELINE_CONTEXT_SELECTION_KEY = "operational_detail_source"
OPERATIONAL_DETAIL_WIDGET_KEY = "operational_detail_source_widget"


def normalize_pipeline_filter(selection: object) -> str:
    """Return the stage vocabulary for current and legacy viewer selections."""
    value = str(selection or "All")
    return LEGACY_FILTER_STAGES.get(value, value)


def selected_pipeline_stage(
    session_state: Mapping[str, object],
) -> str | None:
    """Return an explicitly selected stage identifier, if one exists."""
    selection = normalize_pipeline_filter(
        session_state.get(PIPELINE_CONTEXT_SELECTION_KEY, "All")
    )
    return PIPELINE_STAGE_IDENTIFIERS.get(selection)


def select_pipeline_stage(
    session_state: MutableMapping[str, object],
    stage: str,
) -> None:
    """Record one explicit stage selection without duplicating its value."""
    normalized_stage = normalize_pipeline_filter(stage)
    session_state[PIPELINE_CONTEXT_SELECTION_KEY] = normalized_stage
    session_state[PIPELINE_SELECTION_OVERRIDE_KEY] = (
        normalized_stage != "All"
    )


def synchronize_active_pipeline_stage(
    session_state: MutableMapping[str, object],
    pipeline_run: PipelineRun,
) -> str:
    """Follow PipelineRun unless the user has explicitly selected a stage."""
    selection = normalize_pipeline_filter(
        session_state.get(PIPELINE_CONTEXT_SELECTION_KEY, "All")
    )
    if selection == "All":
        session_state[PIPELINE_SELECTION_OVERRIDE_KEY] = False

    if session_state.get(PIPELINE_SELECTION_OVERRIDE_KEY, False):
        return selection

    active_stage = PIPELINE_IDENTIFIER_STAGES.get(
        pipeline_run.current_stage or ""
    )
    synchronized = active_stage or "All"
    session_state[PIPELINE_CONTEXT_SELECTION_KEY] = synchronized
    return synchronized


def pipeline_stage_context_color(stage: str | None) -> str:
    """Return the established visual context color for one pipeline stage."""
    normalized_stage = normalize_pipeline_filter(stage)
    identifier = PIPELINE_STAGE_IDENTIFIERS.get(
        normalized_stage,
        normalized_stage.lower().replace(" ", ""),
    )
    return PIPELINE_STAGE_CONTEXT_COLORS.get(
        identifier,
        PIPELINE_STAGE_CONTEXT_COLORS["ci"],
    )


def pipeline_source_context_color(source: str | None) -> str:
    """Return the context color assigned to an operational event source."""
    return pipeline_stage_context_color(EVENT_SOURCE_STAGES.get(str(source)))


def event_pipeline_stage(event: OperationalEvent) -> str | None:
    """Associate a normalized operational source with its pipeline stage."""
    return EVENT_SOURCE_STAGES.get(event.source_abbreviation)


def pipeline_stage_source(stage: str) -> str | None:
    """Return the operational source abbreviation for one pipeline stage."""
    return PIPELINE_STAGE_SOURCES.get(stage)


def filter_events_for_stage(
    events: list[OperationalEvent],
    stage: str,
) -> list[OperationalEvent]:
    """Return events associated with one pipeline-stage display name."""
    return [
        event
        for event in events
        if event_pipeline_stage(event) == stage
    ]
