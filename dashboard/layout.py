import html
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from dashboard.pipeline_context import (
    PIPELINE_STAGE_CONTEXT_COLORS,
    pipeline_stage_context_color,
    selected_pipeline_stage,
)

DATA_SOURCE_STATES = {
    "DEMO": "🧪 DEMO",
    "LOCAL": "💻 LOCAL",
    "LIVE": "📡 LIVE",
}
PIPELINE_CONTEXT_ACCENT = PIPELINE_STAGE_CONTEXT_COLORS["ci"]


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
OPERATIONAL_SOURCE_LEGEND = (
    ("GI", "Git"),
    ("GH", "GitHub"),
    ("CI", "CI/CD"),
    ("DB", "Docker Build"),
    ("CR", "GHCR"),
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
    st.html(
        f"""
<style>
:root {{
    --pipeline-context-accent: {context_accent};
}}
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
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.1;
}}
.st-key-pipeline-stage-card-ci .stMarkdownBadge,
.st-key-pipeline-stage-card-ci-selected .stMarkdownBadge {{
    padding-inline: 0.25rem !important;
    font-size: 0.7rem !important;
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


def render_component_header(title: str, data_source_state: str) -> None:
    """Render a component title with its compact data-origin indicator."""
    header = st.container(
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
    """Render the single-line dashboard legend and stable build information."""
    build_information = html.escape(BUILD_INFORMATION)
    source_legend = " · ".join(
        f"{html.escape(abbreviation)} {html.escape(name)}"
        for abbreviation, name in OPERATIONAL_SOURCE_LEGEND
    )
    st.html(
        f"""
<style>
.dashboard-footer-line {{
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    white-space: nowrap;
    color: rgba(128, 128, 128, 0.95);
    font-size: 0.7rem;
    line-height: 1.35;
}}
.dashboard-footer-line .dashboard-footer-legend {{
    flex: 1 1 auto;
}}
.dashboard-footer-line .dashboard-footer-build {{
    flex: 0 0 auto;
    margin-left: auto;
    text-align: right;
}}
</style>
<div class="dashboard-footer-line" role="contentinfo">
  <span class="dashboard-footer-legend">✓ Success · ▶ Running · ◷ Queued · ⚠ Warning · ✕ Failed · — Skipped/Cancelled · ℹ Info | {source_legend} | 🧪 DEMO · 💻 LOCAL · 📡 LIVE</span>
  <span class="dashboard-footer-build">Build {build_information}</span>
</div>
"""
    )
