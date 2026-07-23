import streamlit as st

from dashboard.formatting import format_dashboard_timestamp
from dashboard.layout import render_component_header
from dashboard.operational_detail_viewer import get_ghcr_data


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


def _render_ghcr_card(runtime_snapshot: dict | None = None) -> None:
    with st.container(border=True, height="stretch"):
        render_component_header("Images (GHCR)", "LIVE")
        details = get_ghcr_data(runtime_snapshot)
        availability = details.get("availability")
        if availability != "available":
            status = {
                "missing": "Image unavailable",
                "authentication_unavailable": "Authentication unavailable",
                "unavailable": "Retrieval unavailable",
            }.get(availability, "Retrieval unavailable")
            st.caption(status)
            if details.get("reason"):
                st.caption(details["reason"])
            return

        image_name = details.get("image_name") or "Not available"
        latest_tag = details.get("latest_tag") or "untagged"
        st.markdown(f"**{image_name}:{latest_tag}**")
        if details.get("published_at"):
            st.caption(
                "Published "
                f"{format_dashboard_timestamp(details['published_at'])}"
            )
        if details.get("visibility"):
            st.caption(f"Visibility · {details['visibility']}")
        if details.get("digest"):
            st.caption(f"Digest · {details['digest']}")
        if details.get("package_url"):
            st.link_button("Open GHCR Package", details["package_url"])


def _render_card_row(
    titles: tuple[str, ...],
    runtime_snapshot: dict | None = None,
) -> None:
    columns = st.columns(len(titles), gap="small")
    for column, title in zip(columns, titles, strict=True):
        with column:
            if title == "Images (GHCR)":
                _render_ghcr_card(runtime_snapshot)
            else:
                _render_demo_card(title)


def render_summary_cards() -> None:
    """Render the top-level dashboard summary placeholders."""
    _render_card_row(SUMMARY_CARD_TITLES)


def render_platform_cards(runtime_snapshot: dict | None = None) -> None:
    """Render the dashboard platform placeholder cards."""
    _render_card_row(PLATFORM_CARD_TITLES, runtime_snapshot)
