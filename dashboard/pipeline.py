from pathlib import Path

import streamlit as st

from dashboard.lifecycle import PipelineRun
from dashboard.pipeline_context import (
    select_pipeline_stage,
    selected_pipeline_stage,
)
from dashboard.pipeline_model import PipelineStage, get_pipeline_stages

ASSET_DIRECTORY = Path(__file__).resolve().parent / "assets"
CI_WORKFLOW_ICON = ASSET_DIRECTORY / "ci-workflow.svg"
PIPELINE_STAGE_ICONS = {
    "code": ASSET_DIRECTORY / "code.svg",
    "github": ASSET_DIRECTORY / "github.svg",
    "ci": CI_WORKFLOW_ICON,
    "build": ASSET_DIRECTORY / "docker.svg",
    "ghcr": ASSET_DIRECTORY / "ghcr.svg",
    "argocd": ASSET_DIRECTORY / "argocd.svg",
    "kubernetes": ASSET_DIRECTORY / "kubernetes.svg",
}
PIPELINE_CARD_HEIGHT = 252
PIPELINE_COLUMN_WIDTHS = tuple(
    width
    for index in range(7)
    for width in ((1.0, 0.14) if index < 6 else (1.0,))
)
PIPELINE_STATUS_STYLES = {
    "Completed": ("COMPLETED", "green"),
    "Running": ("RUNNING", "blue"),
    "Failed": ("FAILED", "red"),
    "Unknown": ("UNKNOWN", "gray"),
    "Unavailable": ("UNAVAILABLE", "gray"),
}


def _select_stage(stage: PipelineStage) -> None:
    select_pipeline_stage(st.session_state, stage.display_name)
    st.rerun(scope="app")


def _render_product_icon(
    card,
    icon_path: Path,
    *,
    width: int = 56,
) -> None:
    """Render an optional local product icon without risking the stage card."""
    if not icon_path.is_file():
        return

    try:
        card.image(str(icon_path), width=width)
    except Exception:  # noqa: BLE001 - optional asset failure must stay isolated
        return


def _render_product_stage_card(
    stage: PipelineStage,
    icon_path: Path,
) -> None:
    """Render the shared product-first language for every pipeline stage."""
    card = st.container(
        horizontal_alignment="center",
        vertical_alignment="center",
        gap="small",
    )
    if card.button(
        stage.display_name,
        key=f"pipeline-stage-{stage.identifier}",
        type="tertiary",
        width="content",
    ):
        _select_stage(stage)

    _render_product_icon(card, icon_path, width=56)

    card.caption(
        stage.platform,
        width="content",
        text_alignment="center",
    )

    badge_label, badge_color = PIPELINE_STATUS_STYLES.get(
        stage.status,
        PIPELINE_STATUS_STYLES["Unknown"],
    )
    card.badge(badge_label, color=badge_color)


def _render_transition(index: int) -> None:
    """Render one transition independently from either adjacent stage."""
    st.markdown("→")


def render_delivery_pipeline(
    runtime_snapshot: dict | PipelineRun | None = None,
) -> None:
    """Render the delivery pipeline from the centralized stage model."""
    st.subheader("Delivery Pipeline")
    pipeline_stages = get_pipeline_stages(runtime_snapshot)

    selected_stage = selected_pipeline_stage(st.session_state)
    with st.container(key="delivery-pipeline-grid"):
        pipeline_columns = st.columns(
            PIPELINE_COLUMN_WIDTHS,
            gap="xxsmall",
        )

        for index, stage in enumerate(pipeline_stages):
            card_key = f"pipeline-stage-card-{stage.identifier}"
            if stage.identifier == selected_stage:
                card_key += "-selected"

            with pipeline_columns[index * 2], st.container(
                border=True,
                height=PIPELINE_CARD_HEIGHT,
                key=card_key,
            ):
                _render_product_stage_card(
                    stage,
                    PIPELINE_STAGE_ICONS[stage.identifier],
                )

            if index < len(pipeline_stages) - 1:
                with pipeline_columns[index * 2 + 1]:
                    _render_transition(index)
