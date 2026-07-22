from datetime import datetime

import streamlit as st

from dashboard.formatting import format_dashboard_timestamp


def render_navigation() -> str:
    """Render dashboard navigation and return the selected page identifier."""
    pages = {"🏠 Overview": "overview"}

    st.sidebar.header("Navigation")
    selected_label = st.sidebar.radio(
        "Dashboard pages",
        pages,
        label_visibility="collapsed",
    )

    if "dashboard_loaded_at" not in st.session_state:
        st.session_state.dashboard_loaded_at = datetime.now().astimezone()

    st.sidebar.write("")
    st.sidebar.divider()
    st.sidebar.subheader("Dashboard Status")
    st.sidebar.markdown("**Last Refresh**")
    st.sidebar.caption(format_dashboard_timestamp(st.session_state.dashboard_loaded_at))
    st.sidebar.markdown("**Next Refresh**")
    st.sidebar.caption("Manual")
    st.sidebar.markdown("**Auto Refresh**")
    st.sidebar.caption("OFF")
    st.sidebar.button(
        "Refresh",
        disabled=True,
        help="Manual refresh is not available yet.",
        width="stretch",
    )

    return pages[selected_label]
