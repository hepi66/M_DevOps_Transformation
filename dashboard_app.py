import streamlit as st

from dashboard.deployments import render_deployments
from dashboard.environments import render_environments
from dashboard.layout import render_page_header
from dashboard.navigation import render_navigation
from dashboard.operational_detail_viewer import (
    render_operational_detail_viewer,
    render_status_legend,
)
from dashboard.pipeline import render_delivery_pipeline


st.set_page_config(
    page_title="M-DevOps Dashboard",
    page_icon="📊",
    layout="wide",
)

selected_page = render_navigation()

if selected_page == "overview":
    render_page_header(
        "M-DevOps Dashboard",
        "A professional dashboard for presenting the progress, capabilities, "
        "and outcomes of the M-DevOps Transformation project.",
    )

    with st.container(border=True):
        st.subheader("Architecture Status")
        st.markdown(
            """
- **Modular Dashboard:** Foundation established
- **Dummy Data:** Planned for Phase 1
- **Future GitHub Integration:** Later phase
- **Future Kubernetes Integration:** Later phase
"""
        )

    with st.container(border=True):
        render_delivery_pipeline()

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
            render_operational_detail_viewer()

    with st.container(border=True):
        st.subheader("Dashboard Foundation")
        st.info(
            "This is the foundation of the future DevOps Dashboard, designed "
            "to present the progress, capabilities, and outcomes of the "
            "M-DevOps Transformation project."
        )

    render_status_legend()
