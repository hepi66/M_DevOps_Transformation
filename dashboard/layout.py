import html
import os
from datetime import datetime
from pathlib import Path

import streamlit as st


DATA_SOURCE_STATES = {
    "DEMO": "🧪 DEMO",
    "LOCAL": "💻 LOCAL",
    "LIVE": "📡 LIVE",
}


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


def render_page_header(title: str, description: str) -> None:
    """Render the standard header for a dashboard page."""
    st.title(title)
    st.write(description)
    st.write("")


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
  <span class="dashboard-footer-legend">✓ Success · ▶ Running · ◷ Queued · ⚠ Warning · ✕ Failed · — Skipped/Cancelled · ℹ Info | GI Git · GH GitHub · CI CI/CD | 🧪 DEMO · 💻 LOCAL · 📡 LIVE</span>
  <span class="dashboard-footer-build">Build {build_information}</span>
</div>
"""
    )
