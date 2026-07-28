from collections.abc import Callable
from datetime import datetime

import streamlit as st

from dashboard.formatting import format_dashboard_timestamp


def render_navigation(
    refresh_snapshot: Callable[[], None] | None = None,
    *,
    show_refresh_control: bool = True,
) -> str:
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
    if show_refresh_control:
        st.sidebar.markdown("**Next Refresh**")
        st.sidebar.caption("Manual")
        st.sidebar.markdown("**Auto Refresh**")
        st.sidebar.caption("OFF")
        refresh_requested = st.sidebar.button(
            "Refresh",
            disabled=refresh_snapshot is None,
            help="Reload all dashboard runtime data.",
            width="stretch",
        )
        if refresh_requested and refresh_snapshot is not None:
            refresh_snapshot()
            st.session_state.dashboard_loaded_at = datetime.now().astimezone()
            st.rerun()

    return pages[selected_label]
