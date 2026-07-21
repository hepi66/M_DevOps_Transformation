import streamlit as st


PIPELINE_STAGES = (
    {
        "name": "Code Change",
        "label": "Code",
        "platform": "Developer",
        "platform_label": "Dev",
        "purpose": "A software change is created and committed.",
        "status": "Completed",
    },
    {
        "name": "Source Control",
        "label": "GitHub",
        "platform": "GitHub",
        "platform_label": "GitHub",
        "purpose": "The change is stored, reviewed, and versioned.",
        "status": "Completed",
    },
    {
        "name": "CI & Quality",
        "label": "CI",
        "platform": "GitHub Actions",
        "platform_label": "Actions",
        "purpose": "Automated quality gates validate the change.",
        "status": "Completed",
    },
    {
        "name": "Image Build",
        "label": "Build",
        "platform": "Docker",
        "platform_label": "Docker",
        "purpose": "A deployable container image is created.",
        "status": "Completed",
    },
    {
        "name": "Artifact Registry",
        "label": "GHCR",
        "platform": "GHCR",
        "platform_label": "GHCR",
        "purpose": "The immutable image is published for delivery.",
        "status": "Completed",
    },
    {
        "name": "GitOps Reconciliation",
        "label": "Argo CD",
        "platform": "Argo CD",
        "platform_label": "Argo CD",
        "purpose": "Desired state changes are detected and synchronized.",
        "status": "Active",
    },
    {
        "name": "Runtime",
        "label": "Kubernetes",
        "platform": "Kubernetes",
        "platform_label": "K8s",
        "purpose": "The workload is rolled out and operated.",
        "status": "Upcoming",
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
            st.caption(f"**{stage['label']}**{connector}")
            st.caption(stage["platform_label"])
            st.caption(stage["status"])
