import streamlit as st

from dashboard.layout import render_page_header
from dashboard.navigation import render_navigation


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

    operations_column, logs_column = st.columns([2, 1], gap="medium")

    with operations_column:
        with st.container(border=True):
            st.subheader("Delivery Pipeline")
            st.markdown(
                "This region establishes the primary space for a future "
                "delivery pipeline summary."
            )

        deployments_column, environments_column = st.columns(2, gap="medium")

        with deployments_column:
            with st.container(border=True):
                st.subheader("Deployments")
                st.markdown(
                    "This region defines where deployment information can be "
                    "presented in a later phase."
                )

        with environments_column:
            with st.container(border=True):
                st.subheader("Environments")
                st.markdown(
                    "This region defines where environment information can be "
                    "presented in a later phase."
                )

    with logs_column:
        with st.container(border=True, height="stretch"):
            st.subheader("Log Output")
            st.markdown(
                "This region establishes the visual position of the future "
                "log output viewer. It contains no operational log data."
            )

    with st.container(border=True):
        st.subheader("Dashboard Foundation")
        st.info(
            "This is the foundation of the future DevOps Dashboard, designed "
            "to present the progress, capabilities, and outcomes of the "
            "M-DevOps Transformation project."
        )
