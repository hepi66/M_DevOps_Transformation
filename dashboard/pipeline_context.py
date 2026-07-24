from collections.abc import Mapping

from dashboard.operational_events import OperationalEvent

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
    "code": "#F7E263",
    "github": "#8B5CF6",
    "ci": "#D946EF",
    "build": "#06B6D4",
    "ghcr": "#F59E0B",
    "argocd": "#F97360",
    "kubernetes": "#73B0E7",
}
LEGACY_FILTER_STAGES = {
    "Git / Local Repository": "Code",
    "GitHub Status": "GitHub",
    "Docker Build": "Build",
}
EVENT_SOURCE_STAGES = {
    "GI": "Code",
    "GH": "GitHub",
    "CI": "CI",
    "DB": "Build",
    "CR": "GHCR",
}
PIPELINE_STAGE_SOURCES = {
    stage: source for source, stage in EVENT_SOURCE_STAGES.items()
}


def normalize_pipeline_filter(selection: object) -> str:
    """Return the stage vocabulary for current and legacy viewer selections."""
    value = str(selection or "All")
    return LEGACY_FILTER_STAGES.get(value, value)


def selected_pipeline_stage(
    session_state: Mapping[str, object],
) -> str | None:
    """Return an explicitly selected stage identifier, if one exists."""
    selection = normalize_pipeline_filter(
        session_state.get("operational_detail_source", "All")
    )
    return PIPELINE_STAGE_IDENTIFIERS.get(selection)


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
