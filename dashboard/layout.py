import streamlit as st


def render_page_header(title: str, description: str) -> None:
    """Render the standard header for a dashboard page."""
    st.title(title)
    st.write(description)
    st.write("")
