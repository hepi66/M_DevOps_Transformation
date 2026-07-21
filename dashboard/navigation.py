import streamlit as st


def render_navigation() -> str:
    """Render dashboard navigation and return the selected page identifier."""
    pages = {"🏠 Overview": "overview"}

    st.sidebar.header("Navigation")
    selected_label = st.sidebar.radio(
        "Dashboard pages",
        pages,
        label_visibility="collapsed",
    )

    return pages[selected_label]
