import streamlit as st

from dashboard.layout import render_component_header


ENVIRONMENTS = (
    {
        "environment": "production",
        "status": "Healthy",
        "pods": "12 / 12",
    },
    {
        "environment": "staging",
        "status": "Healthy",
        "pods": "8 / 8",
    },
    {
        "environment": "preview",
        "status": "Deploying",
        "pods": "3 / 4",
    },
    {
        "environment": "development",
        "status": "Healthy",
        "pods": "6 / 6",
    },
)

STATUS_INDICATORS = {
    "Healthy": "🟢",
    "Deploying": "🔵",
}


def render_environments() -> None:
    """Render the static Phase 1 environment demonstration."""
    render_component_header("Environments", "DEMO")
    st.caption("Phase 1 demonstration data")

    for environment in ENVIRONMENTS:
        with st.container(border=True):
            st.caption(
                f"{STATUS_INDICATORS[environment['status']]} "
                f"**{environment['environment']}** · "
                f"{environment['status']} · {environment['pods']} pods"
            )
