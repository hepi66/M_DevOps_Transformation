import streamlit as st

st.set_page_config(
    page_title="M-DevOps Transformation",
    layout="centered"
)

# ------------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------------

st.markdown("""
<style>
div.stButton > button:disabled {
    background-color: #8250df !important;
    color: white !important;
    border: 1px solid #8250df !important;
    opacity: 1 !important;
}

div.stButton > button {
    background-color: #2da44e !important;
    color: white !important;
    border: 1px solid #2da44e !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------

st.title("M-DevOps Transformation Dashboard")

st.write(
    "Visualizing the progress of the DevOps transformation journey."
)

# ------------------------------------------------------------------
# Epic Progress
# ------------------------------------------------------------------

st.header("Epic Progress")

epics = {
    "Foundation": True,
    "Application & Docker": True,
    "CI/CD": True,
    "GitOps & ArgoCD": True,
    "Observability & Demo": False,
}

cols = st.columns(5)

for i, (name, done) in enumerate(epics.items()):
    label = f"{name} ✓" if done else f"{name} 🚧"
    cols[i].button(label, disabled=done)

# ------------------------------------------------------------------
# Engineering Capabilities
# ------------------------------------------------------------------

st.header("Engineering Capabilities")

st.markdown("""
- ✅ Local Development
- ✅ Docker Build
- ✅ Container Registry (GHCR)
- ✅ CI Validation
- ✅ Security Scanning
- ✅ Automated Testing
- ✅ GitOps Deployment
- ✅ ArgoCD Synchronization
- ✅ Operational Validation
""")

# ------------------------------------------------------------------
# DORA Metrics
# ------------------------------------------------------------------

st.header("DORA Metrics")

dora_data = {
    "Metric": [
        "Deployment Frequency",
        "Lead Time for Changes",
        "Change Failure Rate",
        "Mean Time to Restore (MTTR)"
    ],
    "Purpose": [
        "Measure delivery speed",
        "Measure change flow",
        "Measure deployment efficiency",
        "Measure recovery capability"
    ]
}

st.table(dora_data)

# ------------------------------------------------------------------
# Platform Status
# ------------------------------------------------------------------

st.header("Platform Status")

st.success("PASS - Cluster Status")
st.success("PASS - Platform Status")
st.success("PASS - GitOps Status")
st.success("PASS - Application Status")

# ------------------------------------------------------------------
# Architecture Overview
# ------------------------------------------------------------------

st.header("Architecture Overview")

st.code("""
Developer
    ↓
GitHub
    ↓
GitHub Actions
    ↓
GitHub Container Registry (GHCR)
    ↓
ArgoCD
    ↓
Kubernetes
    ↓
Streamlit Application
""")

# ------------------------------------------------------------------
# Value Delivered
# ------------------------------------------------------------------

st.header("Value Delivered")

st.markdown("""
- ✅ Secure Git Repository

- ✅ Dockerized Application

- ✅ Automated CI/CD Pipeline

- ✅ GitOps Deployment with ArgoCD

- ✅ Automated Validation Framework

- ✅ Engineering Knowledge Base
""")

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------

st.divider()

st.caption(
    "M-DevOps Transformation | Epic 0 → Epic 4 | DevOps Product Owner Journey"
)