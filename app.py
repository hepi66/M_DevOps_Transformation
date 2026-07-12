import streamlit as st

st.set_page_config(
    page_title="M-DevOps Transformation",
    layout="wide"
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

journey = [
    "Foundation ✓",
    "Application & Docker ✓",
    "CI/CD ✓",
    "GitOps & ArgoCD ✓",
    "Observability & Demo 🚧"
]

st.markdown(
    " → ".join(journey)
)

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
# DevOps Workflow Simulator
# ------------------------------------------------------------------

import time

st.header("DevOps Workflow Simulator")

if st.button("▶ Start DevOps Workflow"):

    steps = [
        "Developer commits code",
        "GitHub receives push",
        "GitHub Actions started",
        "Linting passed",
        "Security scan passed",
        "Tests passed",
        "Docker image built",
        "Image pushed to GHCR",
        "ArgoCD detected change",
        "Application synchronized",
        "Validation successful",
        "Deployment completed"
    ]

    pipeline_steps = [
        "Developer",
        "GitHub",
        "Actions",
        "GHCR",
        "ArgoCD",
        "Kubernetes",
        "App"
    ]

    stage_details = {
        "Developer": ["Code change", "Git commit"],
        "GitHub": ["Push received", "Repository updated"],
        "Actions": ["Ruff", "Bandit", "pytest"],
        "GHCR": ["Build image", "Push image"],
        "ArgoCD": ["Detect change", "Sync application"],
        "Kubernetes": ["Deploy workload", "Verify health"],
        "App": ["Application running", "Ready for users"]
    }

    progress = st.progress(0)

    pipeline_placeholder = st.empty()
    workflow_placeholder = st.empty()

    status_icons = ["⏳"] * len(steps)

    for current in range(len(steps)):

        if current > 0:
            status_icons[current - 1] = "✅"

        active_stage = min(
            int(current * len(pipeline_steps) / len(steps)),
            len(pipeline_steps) - 1
        )

        with pipeline_placeholder.container():

            left_col, right_col = st.columns([2, 1])

            with left_col:

                st.markdown("### Deployment Pipeline")

                pipeline_lines = []

                for idx, stage in enumerate(pipeline_steps):

                    if idx < active_stage:
                        icon = "✅"
                    elif idx == active_stage:
                        icon = "🔄"
                    else:
                        icon = "⏳"

                    pipeline_lines.append(f"{icon} {stage}")

                    if idx < len(pipeline_steps) - 1:
                        pipeline_lines.append("⬇️")

                st.markdown("\n\n".join(pipeline_lines))

            with right_col:

                current_stage = pipeline_steps[active_stage]

                st.markdown("### Current Stage")

                st.info(current_stage)

                st.markdown("#### Tasks")

                for task in stage_details[current_stage]:
                    st.write(f"• {task}")

        lines = []

        for idx, step in enumerate(steps):

            icon = status_icons[idx]

            if idx == current:
                icon = "🔄"

            lines.append(f"{icon} {step}")

        workflow_placeholder.markdown(
            "### Workflow Status\n\n" +
            "\n\n".join(lines)
        )

        progress.progress((current + 1) / len(steps))

        time.sleep(0.5)

    with pipeline_placeholder.container():

        left_col, right_col = st.columns([2, 1])

        with left_col:

            st.markdown("### Deployment Pipeline")

            final_pipeline = []

            for idx, stage in enumerate(pipeline_steps):

                final_pipeline.append(f"✅ {stage}")

                if idx < len(pipeline_steps) - 1:
                    final_pipeline.append("⬇️")

            st.markdown("\n\n".join(final_pipeline))

        with right_col:

            st.markdown("### Current Stage")

            st.success("Completed")

            st.markdown("#### Result")

            st.write("• Deployment successful")
            st.write("• Application running")
            st.write("• GitOps synchronized")

    final_lines = [f"✅ {step}" for step in steps]

    workflow_placeholder.markdown(
        "### Workflow Status\n\n" +
        "\n\n".join(final_lines)
    )

    st.success("DevOps workflow completed successfully.")

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