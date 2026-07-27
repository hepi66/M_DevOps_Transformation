import streamlit as st

from dashboard.deployments import render_deployments
from dashboard.environments import render_environments
from dashboard.layout import (
    render_dashboard_footer,
    render_dashboard_styles,
    render_page_header,
)
from dashboard.lifecycle import aggregate_pipeline_run
from dashboard.navigation import render_navigation
from dashboard.operational_detail_viewer import (
    clear_dashboard_snapshot,
    load_dashboard_snapshot,
    render_operational_detail_viewer,
)
from dashboard.overview_cards import render_platform_cards, render_summary_cards
from dashboard.pipeline import render_delivery_pipeline

st.set_page_config(
    page_title="M-DevOps Dashboard",
    page_icon="📊",
    layout="wide",
)
render_dashboard_styles()

selected_page = render_navigation(clear_dashboard_snapshot)

if selected_page == "overview":
    with st.spinner("Loading dashboard data..."):
        runtime_snapshot = load_dashboard_snapshot()
        pipeline_run = aggregate_pipeline_run(runtime_snapshot)

    render_page_header(
        "M-DevOps Dashboard",
        "A professional dashboard for presenting the progress, capabilities, "
        "and outcomes of the M-DevOps Transformation project.",
    )

    render_summary_cards()

    with st.container(border=True):
        render_delivery_pipeline(pipeline_run)

    overview_column, logs_column = st.columns(
        [1, 2],
        gap="medium",
    )

    with overview_column:
        with st.container(border=True, height="stretch"):
            render_deployments()

        with st.container(border=True, height="stretch"):
            render_environments()

    with logs_column, st.container(
        border=True,
        height="stretch",
        key="operational-detail-viewer-card",
    ):
        render_operational_detail_viewer(runtime_snapshot)

    render_platform_cards(runtime_snapshot)

    render_dashboard_footer()
