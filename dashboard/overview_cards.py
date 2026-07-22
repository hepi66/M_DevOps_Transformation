import streamlit as st

from dashboard.layout import render_component_header


SUMMARY_CARD_TITLES = (
    "Deployment Frequency",
    "Lead Time for Changes",
    "Change Failure Rate",
    "Mean Time to Restore",
    "System Health",
)

PLATFORM_CARD_TITLES = (
    "Active Alerts",
    "DORA Metrics Trend",
    "Images (GHCR)",
    "Cluster Summary",
)


def _render_demo_card(title: str) -> None:
    with st.container(border=True, height="stretch"):
        render_component_header(title, "DEMO")
        st.caption("Awaiting data source")


def _render_card_row(titles: tuple[str, ...]) -> None:
    columns = st.columns(len(titles), gap="small")
    for column, title in zip(columns, titles, strict=True):
        with column:
            _render_demo_card(title)


def render_summary_cards() -> None:
    """Render the top-level dashboard summary placeholders."""
    _render_card_row(SUMMARY_CARD_TITLES)


def render_platform_cards() -> None:
    """Render the dashboard platform placeholder cards."""
    _render_card_row(PLATFORM_CARD_TITLES)
