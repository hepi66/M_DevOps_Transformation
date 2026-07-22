import streamlit as st

from dashboard.layout import render_component_header


DEPLOYMENTS = (
    {
        "environment": "production",
        "status": "Healthy",
        "version": "v1.24.7",
    },
    {
        "environment": "staging",
        "status": "Deploying",
        "version": "v1.24.8",
    },
    {
        "environment": "development",
        "status": "Testing",
        "version": "v1.24.9",
    },
)

STATUS_INDICATORS = {
    "Healthy": "🟢",
    "Deploying": "🔵",
    "Testing": "🟡",
}


def render_deployments() -> None:
    """Render the static Phase 1 deployment demonstration."""
    render_component_header("Deployments", "DEMO")
    st.caption("Phase 1 demonstration data")

    for deployment in DEPLOYMENTS:
        with st.container(border=True):
            st.caption(
                f"{STATUS_INDICATORS[deployment['status']]} "
                f"**{deployment['environment']}** · "
                f"{deployment['status']} · {deployment['version']}"
            )
