import streamlit as st

from dashboard.deployments import render_deployments
from dashboard.environments import render_environments
from dashboard.layout import (
    render_dashboard_footer,
    render_page_header,
)
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

selected_page = render_navigation(clear_dashboard_snapshot)

if selected_page == "overview":
    with st.spinner("Loading dashboard data..."):
        runtime_snapshot = load_dashboard_snapshot()

    render_page_header(
        "M-DevOps Dashboard",
        "A professional dashboard for presenting the progress, capabilities, "
        "and outcomes of the M-DevOps Transformation project.",
    )

    render_summary_cards()

    with st.container(border=True):
        render_delivery_pipeline(runtime_snapshot)

    deployments_column, environments_column, logs_column = st.columns(
        3,
        gap="medium",
    )

    with deployments_column:
        with st.container(border=True, height="stretch"):
            render_deployments()

    with environments_column:
        with st.container(border=True, height="stretch"):
            render_environments()

    with logs_column:
        with st.container(border=True, height="stretch"):
            render_operational_detail_viewer(runtime_snapshot)

    render_platform_cards(runtime_snapshot)

    render_dashboard_footer()
