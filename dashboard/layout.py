import html
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from dashboard.pipeline_context import (
    OPERATIONAL_SOURCES,
    PIPELINE_STAGE_CONTEXT_COLORS,
    pipeline_stage_context_color,
    selected_pipeline_stage,
)

DATA_SOURCE_STATES = {
    "DEMO": "🧪 DEMO",
    "LOCAL": "💻 LOCAL",
    "LIVE": "📡 LIVE",
}
SEMANTIC_STATUS_COLORS = {
    "success": "#22C55E",
    "active": "#3B82F6",
    "validation": "#EAB308",
}
STATUS_PRESENTATION = {
    "healthy": {
        "label": "Healthy",
        "semantic": "success",
        "symbol": "✓",
        "color": SEMANTIC_STATUS_COLORS["success"],
    },
    "deploying": {
        "label": "Deploying",
        "semantic": "active",
        "symbol": "▶",
        "color": SEMANTIC_STATUS_COLORS["active"],
    },
    "testing": {
        "label": "Testing",
        "semantic": "validation",
        "symbol": "◷",
        "color": SEMANTIC_STATUS_COLORS["validation"],
    },
}
PIPELINE_CONTEXT_ACCENT = PIPELINE_STAGE_CONTEXT_COLORS["ci"]


def status_presentation(status: str) -> dict[str, str]:
    """Return the centralized presentation for a supported dashboard status."""
    normalized_status = status.strip().lower()
    if normalized_status not in STATUS_PRESENTATION:
        raise ValueError(f"Unsupported dashboard status: {status}")
    return STATUS_PRESENTATION[normalized_status]


def _resolve_build_information() -> str:
    configured_timestamp = os.environ.get("DASHBOARD_BUILD_TIMESTAMP")
    if configured_timestamp:
        return configured_timestamp

    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch:
        try:
            return datetime.fromtimestamp(
                int(source_date_epoch),
            ).astimezone().strftime("%Y-%m-%d %H:%M")
        except ValueError:
            pass

    dashboard_entry_point = Path(__file__).resolve().parent.parent / "dashboard_app.py"
    return datetime.fromtimestamp(
        dashboard_entry_point.stat().st_mtime,
    ).astimezone().strftime("%Y-%m-%d %H:%M")


BUILD_INFORMATION = _resolve_build_information()
OPERATIONAL_SOURCE_LEGEND = tuple(
    (source, definition["label"])
    for source, definition in OPERATIONAL_SOURCES.items()
)
STATUS_LEGEND = (
    ("&#10003;", "Success"),
    ("&#9654;", "Running"),
    ("&#9719;", "Queued"),
    ("&#9888;", "Warning"),
    ("&#10005;", "Failed"),
    ("&mdash;", "Skipped/Cancelled"),
)


def render_page_header(title: str, description: str) -> None:
    """Render the standard header for a dashboard page."""
    st.title(title)
    st.write(description)
    st.write("")


def render_dashboard_styles() -> None:
    """Render centralized presentation rules shared across dashboard regions."""
    context_accent = pipeline_stage_context_color(
        selected_pipeline_stage(st.session_state)
    )
    stage_title_accent_rules = "\n".join(
        (
            f'[class*="st-key-pipeline-stage-card-{identifier}"] {{\n'
            f"    --pipeline-stage-title-accent: {color};\n"
            "}"
        )
        for identifier, color in PIPELINE_STAGE_CONTEXT_COLORS.items()
    )
    st.html(
        f"""
<style>
:root {{
    --pipeline-context-accent: {context_accent};
}}
{stage_title_accent_rules}
[class*="st-key-pipeline-stage-card-"][class*="-selected"] {{
    border-color: var(--pipeline-context-accent) !important;
    box-shadow:
        inset 0 0 0 1px var(--pipeline-context-accent),
        0 0 0.75rem color-mix(
            in srgb,
            var(--pipeline-context-accent) 20%,
            transparent
        );
}}
.st-key-operational-detail-viewer-card:has(
    .st-key-operational-detail-viewer-selected
) {{
    border-color: var(--pipeline-context-accent) !important;
    box-shadow:
        0 0 0.75rem color-mix(
            in srgb,
            var(--pipeline-context-accent) 20%,
            transparent
        );
}}
.st-key-operational-detail-viewer-selected {{
    border: 0 !important;
    box-shadow: none !important;
}}
[class*="st-key-pipeline-stage-card-"]
[class*="st-key-pipeline-stage-"] button p {{
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.1;
}}
[class*="st-key-pipeline-stage-card-"]
[class*="st-key-pipeline-stage-"] button:hover p,
[class*="st-key-pipeline-stage-card-"]
[class*="st-key-pipeline-stage-"] button:active p,
[class*="st-key-pipeline-stage-card-"]
[class*="st-key-pipeline-stage-"] button:focus p {{
    color: var(--pipeline-stage-title-accent) !important;
}}
.stHeading h3 {{
    font-size: 1.5rem;
}}
.st-key-delivery-pipeline-grid .stMarkdownBadge {{
    padding-inline: 0.25rem !important;
    font-size: 0.875rem !important;
    line-height: 1.2 !important;
    width: max-content !important;
    max-width: none !important;
}}
.st-key-delivery-pipeline-grid p:has(.stMarkdownBadge) {{
    width: max-content !important;
    max-width: none !important;
}}
.st-key-delivery-pipeline-grid
> [data-testid="stLayoutWrapper"]
> [data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(even)
> [data-testid="stVerticalBlock"] {{
    height: 300px;
    justify-content: center;
}}
.st-key-delivery-pipeline-grid
> [data-testid="stLayoutWrapper"]
> [data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(even) p {{
    margin: 0;
    color: rgba(128, 128, 128, 0.9);
    font-size: 1.4rem;
    line-height: 1;
    text-align: center;
    transform: translateY(-0.5rem);
}}
</style>
"""
    )


def render_component_header(
    title: str,
    data_source_state: str,
    *,
    key: str | None = None,
) -> None:
    """Render a component title with its compact data-origin indicator."""
    header = st.container(
        key=key,
        horizontal=True,
        horizontal_alignment="distribute",
        vertical_alignment="center",
        gap="small",
    )
    header.subheader(title, width="stretch")
    render_data_source_indicator(data_source_state, header)


def render_data_source_indicator(data_source_state: str, container=st) -> None:
    """Render a compact data-origin indicator in the supplied container."""
    normalized_state = data_source_state.upper()
    if normalized_state not in DATA_SOURCE_STATES:
        raise ValueError(f"Unsupported data source state: {data_source_state}")

    container.caption(DATA_SOURCE_STATES[normalized_state], width="content")


def render_dashboard_footer() -> None:
    """Render a responsive dashboard legend and stable build information."""
    build_information = html.escape(BUILD_INFORMATION)
    status_legend = "".join(
        f'<span class="dashboard-footer-item">{symbol} {label}</span>'
        for symbol, label in STATUS_LEGEND
    )
    source_legend = "".join(
        '<span class="dashboard-footer-item">'
        f"{html.escape(abbreviation)} {html.escape(name)}</span>"
        for abbreviation, name in OPERATIONAL_SOURCE_LEGEND
    )
    st.html(
        f"""
<style>
.dashboard-footer-line {{
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem 1rem;
    width: 100%;
    color: rgba(128, 128, 128, 0.95);
    font-size: 0.7rem;
    line-height: 1.35;
}}
.dashboard-footer-legends {{
    display: flex;
    flex: 1 1 42rem;
    flex-wrap: wrap;
    gap: 0.45rem 1.25rem;
    min-width: 0;
}}
.dashboard-footer-group {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 0.7rem;
}}
.dashboard-footer-group-label {{
    font-weight: 600;
    color: rgba(160, 160, 160, 0.95);
}}
.dashboard-footer-item {{
    white-space: nowrap;
}}
.dashboard-footer-line .dashboard-footer-build {{
    flex: 0 0 auto;
    margin-left: auto;
    text-align: right;
}}
</style>
<div class="dashboard-footer-line" role="contentinfo">
  <div class="dashboard-footer-legends">
    <div class="dashboard-footer-group" aria-label="Status legend">
      <span class="dashboard-footer-group-label">Status</span>
      {status_legend}
    </div>
    <div class="dashboard-footer-group" aria-label="Source legend">
      <span class="dashboard-footer-group-label">Sources</span>
      {source_legend}
    </div>
    <div class="dashboard-footer-group" aria-label="Data source legend">
      <span class="dashboard-footer-group-label">Data</span>
      <span class="dashboard-footer-item">DEMO</span>
      <span class="dashboard-footer-item">LOCAL</span>
      <span class="dashboard-footer-item">LIVE</span>
    </div>
  </div>
  <span class="dashboard-footer-build">Build {build_information}</span>
</div>
"""
    )
