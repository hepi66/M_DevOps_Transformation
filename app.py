import streamlit as st

st.set_page_config(page_title="M-DevOps Transformation", layout="centered")

# CSS Injection zur individuellen Farbanpassung der Buttons
st.markdown("""
    <style>
    /* Done Buttons (Violett) */
    div.stButton > button:disabled {
        background-color: #8250df !important;
        color: white !important;
        border: 1px solid #8250df !important;
        opacity: 1 !important;
    }
    /* Todo Buttons (Grün) */
    div.stButton > button {
        background-color: #2da44e !important;
        color: white !important;
        border: 1px solid #2da44e !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("M-DevOps Transformation Dashboard")
st.write("Visualizing the progress of our DevOps journey.")

epic_status = {
    "Epic 0": True,
    "Epic 1": True,
    "Epic 2": False,
    "Epic 3": False,
    "Epic 4": False,
}

cols = st.columns(5)
for i, (name, is_done) in enumerate(epic_status.items()):
    label = f"{name} (Done)" if is_done else f"{name} (Todo)"
    
    # Der Button-Befehl bleibt gleich, das Design steuert jetzt das CSS oben
    cols[i].button(label, disabled=is_done)