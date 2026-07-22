import streamlit as st

from dashboard.layout import render_data_source_indicator


PIPELINE_STAGES = (
    {
        "name": "Code Change",
        "label": "Code",
        "platform": "Developer",
        "platform_label": "Dev",
        "purpose": "A software change is created and committed.",
        "status": "Completed",
        "data_source_state": "LOCAL",
    },
    {
        "name": "Source Control",
        "label": "GitHub",
        "platform": "GitHub",
        "platform_label": "GitHub",
        "purpose": "The change is stored, reviewed, and versioned.",
        "status": "Completed",
        "data_source_state": "LIVE",
    },
    {
        "name": "CI & Quality",
        "label": "CI",
        "platform": "GitHub Actions",
        "platform_label": "Actions",
        "purpose": "Automated quality gates validate the change.",
        "status": "Completed",
        "data_source_state": "LIVE",
    },
    {
        "name": "Image Build",
        "label": "Build",
        "platform": "Docker",
        "platform_label": "Docker",
        "purpose": "A deployable container image is created.",
        "status": "Completed",
        "data_source_state": "LOCAL",
    },
    {
        "name": "Artifact Registry",
        "label": "GHCR",
        "platform": "GHCR",
        "platform_label": "GHCR",
        "purpose": "The immutable image is published for delivery.",
        "status": "Completed",
        "data_source_state": "LIVE",
    },
    {
        "name": "GitOps Reconciliation",
        "label": "Argo CD",
        "platform": "Argo CD",
        "platform_label": "Argo CD",
        "purpose": "Desired state changes are detected and synchronized.",
        "status": "Active",
        "data_source_state": "DEMO",
    },
    {
        "name": "Runtime",
        "label": "Kubernetes",
        "platform": "Kubernetes",
        "platform_label": "K8s",
        "purpose": "The workload is rolled out and operated.",
        "status": "Upcoming",
        "data_source_state": "DEMO",
    },
)


def render_delivery_pipeline() -> None:
    """Render the static Phase 1 delivery pipeline demonstration."""
    st.subheader("Delivery Pipeline")
    st.caption("Phase 1 demonstration data")

    pipeline_columns = st.columns(
        len(PIPELINE_STAGES),
        gap="xxsmall",
        border=True,
    )

    for index, stage in enumerate(PIPELINE_STAGES):
        connector = " →" if index < len(PIPELINE_STAGES) - 1 else ""

        with pipeline_columns[index]:
            _, stage_header = st.columns([1, 5], gap="xxsmall")
            render_data_source_indicator(
                stage["data_source_state"],
                stage_header,
            )
            st.caption(f"**{stage['label']}**{connector}")
            st.caption(f"{stage['platform_label']} · {stage['status']}")
