import streamlit as st

from dashboard.layout import render_data_source_indicator
from dashboard.pipeline_model import get_pipeline_stages


def render_delivery_pipeline(runtime_snapshot: dict | None = None) -> None:
    """Render the static Phase 1 delivery pipeline demonstration."""
    st.subheader("Delivery Pipeline")
    st.caption("Phase 1 demonstration data")
    pipeline_stages = get_pipeline_stages(runtime_snapshot)

    pipeline_columns = st.columns(
        len(pipeline_stages),
        gap="xxsmall",
        border=True,
    )

    for index, stage in enumerate(pipeline_stages):
        connector = " →" if index < len(pipeline_stages) - 1 else ""

        with pipeline_columns[index]:
            _, stage_header = st.columns([1, 5], gap="xxsmall")
            render_data_source_indicator(
                stage.source_classification,
                stage_header,
            )
            if stage.detail_view:
                if st.button(
                    f"{stage.display_name}{connector}",
                    key=f"pipeline-stage-{stage.identifier}",
                    type="tertiary",
                ):
                    st.session_state["operational_detail_source"] = stage.detail_view
                    st.rerun()
            else:
                st.caption(f"**{stage.display_name}**{connector}")
            st.caption(f"{stage.platform_label} · {stage.status}")
