import streamlit as st

from dashboard.deployment_page import (
    deployment_monitoring_status_text,
    render_deployment_page,
)
from dashboard.deployments import render_deployments
from dashboard.environments import render_environments
from dashboard.layout import (
    render_dashboard_footer,
    render_dashboard_styles,
    render_page_header,
)
from dashboard.monitoring import (
    MONITORING_STATE_KEY,
    MonitoringState,
    automatic_refresh_interval,
    ensure_monitoring_state,
    render_live_refresh_control,
    render_monitoring_status,
    request_monitoring_refresh,
)
from dashboard.navigation import render_navigation
from dashboard.operational_detail_viewer import (
    render_operational_detail_viewer,
)
from dashboard.overview_cards import render_platform_cards, render_summary_cards
from dashboard.pipeline import render_delivery_pipeline
from dashboard.pipeline_context import synchronize_active_pipeline_stage

st.set_page_config(
    page_title="M-DevOps Dashboard",
    page_icon="📊",
    layout="wide",
)
render_dashboard_styles()

selected_page = render_navigation(show_refresh_control=False)
live_refresh = render_live_refresh_control()
fragment_interval = automatic_refresh_interval(live_refresh)


@st.fragment(run_every=fragment_interval)
def render_pipeline_monitoring_fragment() -> MonitoringState:
    """Refresh and render only the shared live-monitoring pipeline area."""
    monitoring_state = ensure_monitoring_state(automatic=live_refresh)
    synchronize_active_pipeline_stage(
        st.session_state,
        monitoring_state.pipeline_run,
    )
    render_dashboard_styles()
    with st.container(border=True):
        if render_monitoring_status(
            monitoring_state,
            automatic=live_refresh,
        ):
            request_monitoring_refresh()
            st.rerun()
        render_delivery_pipeline(monitoring_state.pipeline_run)
    return monitoring_state


@st.fragment(run_every=fragment_interval)
def render_operational_monitoring_fragment() -> None:
    """Render the viewer from the same scheduled monitoring observation."""
    monitoring_state = ensure_monitoring_state(automatic=live_refresh)
    synchronize_active_pipeline_stage(
        st.session_state,
        monitoring_state.pipeline_run,
    )
    render_operational_detail_viewer(
        monitoring_state.snapshot,
        monitoring_state.pipeline_run,
    )


@st.fragment(run_every=fragment_interval)
def render_deployment_page_fragment() -> None:
    """Render the Deployments page from one shared monitoring observation."""
    monitoring_state = ensure_monitoring_state(automatic=live_refresh)
    render_dashboard_styles()
    if render_monitoring_status(
        monitoring_state,
        automatic=live_refresh,
        status_text=deployment_monitoring_status_text(
            monitoring_state,
            automatic=live_refresh,
        ),
    ):
        request_monitoring_refresh()
        st.rerun()
    render_deployment_page(monitoring_state)

if selected_page == "overview":
    render_page_header(
        "M-DevOps Dashboard",
        "A professional dashboard for presenting the progress, capabilities, "
        "and outcomes of the M-DevOps Transformation project.",
    )

    render_summary_cards()

    monitoring_state = render_pipeline_monitoring_fragment()

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
        render_operational_monitoring_fragment()

    current_monitoring_state = st.session_state.get(MONITORING_STATE_KEY)
    platform_snapshot = (
        current_monitoring_state.snapshot
        if isinstance(current_monitoring_state, MonitoringState)
        else monitoring_state.snapshot
    )
    render_platform_cards(platform_snapshot)

    render_dashboard_footer()

elif selected_page == "deployments":
    render_page_header(
        "Deployments",
        "A live view of the currently deployed M-DevOps Dashboard release, "
        "its immutable artifact identity, GitOps state, Kubernetes runtime, "
        "and access path.",
    )
    render_deployment_page_fragment()
    render_dashboard_footer()
