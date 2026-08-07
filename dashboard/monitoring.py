from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import streamlit as st

from dashboard.cluster_providers import (
    load_cluster_observations,
    provider_snapshot,
)
from dashboard.formatting import format_dashboard_timestamp
from dashboard.lifecycle import (
    ArgoCDProviderData,
    KubernetesProviderData,
    PipelineRun,
    aggregate_pipeline_run,
)
from dashboard.operational_detail_viewer import (
    clear_dashboard_snapshot,
    load_dashboard_snapshot,
)

SnapshotLoader = Callable[[], dict]
ClusterLoader = Callable[
    [],
    tuple[ArgoCDProviderData, KubernetesProviderData],
]


@dataclass(frozen=True)
class RefreshPolicy:
    """Deterministic provider scheduling policy in seconds."""

    idle_seconds: int = 45
    active_seconds: int = 7
    unavailable_seconds: int = 20
    countdown_seconds: int = 1


DEFAULT_REFRESH_POLICY = RefreshPolicy()
MONITORING_STATE_KEY = "dashboard_monitoring_state"
FORCE_REFRESH_KEY = "dashboard_monitoring_force_refresh"
LIVE_REFRESH_KEY = "dashboard_live_refresh"


@dataclass(frozen=True)
class MonitoringState:
    """One authoritative live-monitoring observation and its schedule."""

    snapshot: dict
    pipeline_run: PipelineRun
    last_attempt: datetime
    last_success: datetime | None
    next_refresh: datetime
    retrieval_failed: bool = False
    retrieval_error: str | None = None
    ghcr_stability_cycles_remaining: int = 1


def _same_pipeline_execution(
    previous: PipelineRun,
    current: PipelineRun,
) -> bool:
    """Return whether two observations describe the same immutable CI run."""
    return bool(
        previous.commit_sha
        and previous.commit_sha == current.commit_sha
        and previous.workflow_run_id
        and previous.workflow_run_id == current.workflow_run_id
    )


def _stabilize_transient_ghcr_evidence(
    snapshot: dict,
    pipeline_run: PipelineRun,
    previous: MonitoringState | None,
) -> tuple[dict, int]:
    """Retain one last correlated GHCR observation for one transient cycle."""
    ghcr_stage = pipeline_run.stage("ghcr")
    if ghcr_stage and ghcr_stage.status == "Completed":
        return snapshot, 1

    if previous is None or previous.ghcr_stability_cycles_remaining <= 0:
        return snapshot, 0

    previous_stage = previous.pipeline_run.stage("ghcr")
    if (
        previous_stage is None
        or previous_stage.status != "Completed"
        or ghcr_stage is None
        or ghcr_stage.status not in {"Unknown", "Unavailable"}
        or not _same_pipeline_execution(previous.pipeline_run, pipeline_run)
        or pipeline_run.ghcr.status == "failed"
        or pipeline_run.ghcr.availability
        in {"missing", "authentication_unavailable"}
    ):
        return snapshot, 0

    previous_ghcr = previous.snapshot.get("ghcr")
    if not isinstance(previous_ghcr, dict):
        return snapshot, 0

    stabilized = dict(snapshot)
    stabilized["ghcr"] = dict(previous_ghcr)
    return stabilized, previous.ghcr_stability_cycles_remaining - 1


def refresh_interval_for(
    pipeline_run: PipelineRun,
    *,
    retrieval_failed: bool = False,
    policy: RefreshPolicy = DEFAULT_REFRESH_POLICY,
) -> int:
    """Select a small adaptive interval from real lifecycle state."""
    if retrieval_failed or pipeline_run.refresh_status == "unavailable":
        return policy.unavailable_seconds
    if pipeline_run.workflow_status in {"queued", "running"} or any(
        stage.status in {"Active", "Running", "Queued"}
        for stage in pipeline_run.stages
    ):
        return policy.active_seconds
    if pipeline_run.refresh_status == "partial":
        return policy.unavailable_seconds
    return policy.idle_seconds


def refresh_monitoring_state(
    previous: MonitoringState | None = None,
    *,
    now: datetime | None = None,
    snapshot_loader: SnapshotLoader = load_dashboard_snapshot,
    cluster_loader: ClusterLoader = load_cluster_observations,
    clear_snapshot: Callable[[], None] = clear_dashboard_snapshot,
    policy: RefreshPolicy = DEFAULT_REFRESH_POLICY,
) -> MonitoringState:
    """Retrieve providers once and produce one authoritative PipelineRun."""
    attempted_at = now or datetime.now(timezone.utc)
    try:
        clear_snapshot()
        snapshot = dict(snapshot_loader())
        argocd, kubernetes = cluster_loader()
        completed_at = now or datetime.now(timezone.utc)
        snapshot.update(provider_snapshot(argocd, kubernetes))
        snapshot["refreshed_at"] = completed_at.isoformat()
        provisional_run = aggregate_pipeline_run(
            snapshot,
            argocd_observation=argocd,
            kubernetes_observation=kubernetes,
        )
        retrieved_snapshot = snapshot
        snapshot, ghcr_stability_cycles = _stabilize_transient_ghcr_evidence(
            snapshot,
            provisional_run,
            previous,
        )
        if snapshot is not retrieved_snapshot:
            provisional_run = aggregate_pipeline_run(
                snapshot,
                argocd_observation=argocd,
                kubernetes_observation=kubernetes,
            )
        interval = refresh_interval_for(
            provisional_run,
            policy=policy,
        )
        pipeline_run = aggregate_pipeline_run(
            snapshot,
            argocd_observation=argocd,
            kubernetes_observation=kubernetes,
            refresh_interval_seconds=interval,
        )
        return MonitoringState(
            snapshot=snapshot,
            pipeline_run=pipeline_run,
            last_attempt=attempted_at,
            last_success=completed_at,
            next_refresh=completed_at + timedelta(seconds=interval),
            ghcr_stability_cycles_remaining=ghcr_stability_cycles,
        )
    except Exception as error:  # noqa: BLE001 - preserve last safe observation
        interval = policy.unavailable_seconds
        if previous is not None:
            return MonitoringState(
                snapshot=previous.snapshot,
                pipeline_run=previous.pipeline_run,
                last_attempt=attempted_at,
                last_success=previous.last_success,
                next_refresh=attempted_at + timedelta(seconds=interval),
                retrieval_failed=True,
                retrieval_error=(
                    f"Live data retrieval failed: {type(error).__name__}."
                ),
                ghcr_stability_cycles_remaining=(
                    previous.ghcr_stability_cycles_remaining
                ),
            )

        fallback_snapshot = {
            "state": "Not available",
            "reason": "Live data retrieval is unavailable.",
            "refreshed_at": attempted_at.isoformat(),
        }
        fallback_run = aggregate_pipeline_run(
            fallback_snapshot,
            refresh_interval_seconds=interval,
        )
        return MonitoringState(
            snapshot=fallback_snapshot,
            pipeline_run=fallback_run,
            last_attempt=attempted_at,
            last_success=None,
            next_refresh=attempted_at + timedelta(seconds=interval),
            retrieval_failed=True,
            retrieval_error=(
                f"Live data retrieval failed: {type(error).__name__}."
            ),
            ghcr_stability_cycles_remaining=0,
        )


def ensure_monitoring_state(
    *,
    now: datetime | None = None,
    automatic: bool = True,
) -> MonitoringState:
    """Refresh only when due, otherwise reuse the current observation."""
    current_time = now or datetime.now(timezone.utc)
    current = st.session_state.get(MONITORING_STATE_KEY)
    force_refresh = bool(st.session_state.get(FORCE_REFRESH_KEY, False))
    due = (
        not isinstance(current, MonitoringState)
        or current_time >= current.next_refresh
    )
    if force_refresh or (automatic and due) or not isinstance(
        current,
        MonitoringState,
    ):
        current = refresh_monitoring_state(
            current if isinstance(current, MonitoringState) else None,
            now=current_time,
        )
        st.session_state[MONITORING_STATE_KEY] = current
        st.session_state[FORCE_REFRESH_KEY] = False
    return current


def live_refresh_enabled() -> bool:
    """Return the global automatic scheduling mode, enabled by default."""
    return bool(st.session_state.get(LIVE_REFRESH_KEY, True))


def automatic_refresh_interval(
    enabled: bool,
    *,
    policy: RefreshPolicy = DEFAULT_REFRESH_POLICY,
) -> int | None:
    """Return fragment scheduling only while Live Refresh is enabled."""
    return policy.countdown_seconds if enabled else None


def render_live_refresh_control() -> bool:
    """Render the global development refresh mode in the sidebar."""
    enabled = st.sidebar.toggle(
        "Live Refresh",
        value=live_refresh_enabled(),
        key=LIVE_REFRESH_KEY,
        help="Enable adaptive automatic monitoring updates.",
    )
    st.sidebar.caption(
        "ON · Adaptive monitoring"
        if enabled
        else "OFF · Manual refresh only"
    )
    return bool(enabled)


def request_monitoring_refresh(
    *,
    now: datetime | None = None,
) -> None:
    """Mark the shared monitoring observation due immediately."""
    st.session_state[FORCE_REFRESH_KEY] = True
    current = st.session_state.get(MONITORING_STATE_KEY)
    if isinstance(current, MonitoringState):
        current_time = now or datetime.now(timezone.utc)
        st.session_state[MONITORING_STATE_KEY] = MonitoringState(
            snapshot=current.snapshot,
            pipeline_run=current.pipeline_run,
            last_attempt=current.last_attempt,
            last_success=current.last_success,
            next_refresh=current_time,
            retrieval_failed=current.retrieval_failed,
            retrieval_error=current.retrieval_error,
            ghcr_stability_cycles_remaining=(
                current.ghcr_stability_cycles_remaining
            ),
        )


def seconds_until_refresh(
    state: MonitoringState,
    *,
    now: datetime | None = None,
) -> int:
    """Return the real remaining schedule delay for the countdown."""
    current_time = now or datetime.now(timezone.utc)
    return max(0, int((state.next_refresh - current_time).total_seconds()))


def monitoring_status_text(
    state: MonitoringState,
    *,
    now: datetime | None = None,
    automatic: bool = True,
) -> str:
    """Return compact English monitoring status text."""
    if not automatic:
        return "Live refresh paused · Manual updates only"
    remaining = seconds_until_refresh(state, now=now)
    if (
        state.retrieval_failed
        or state.pipeline_run.refresh_status in {"partial", "unavailable"}
    ):
        return f"Data unavailable · Retry in {remaining}s"
    if state.pipeline_run.workflow_status in {"queued", "running"}:
        return f"Active run · Next refresh in {remaining}s"
    return f"Idle · Next check in {remaining}s"


def render_monitoring_status(
    state: MonitoringState,
    *,
    automatic: bool = True,
    status_text: str | None = None,
) -> bool:
    """Render refresh state and return whether manual refresh was requested."""
    status_column, updated_column, action_column = st.columns(
        [1.2, 1.2, 0.6],
        gap="small",
        vertical_alignment="center",
    )
    status_column.caption(
        status_text or monitoring_status_text(state, automatic=automatic)
    )
    updated_column.caption(
        "Last updated: "
        + (
            format_dashboard_timestamp(state.last_success)
            if state.last_success
            else "Not available"
        )
    )
    return action_column.button(
        "Refresh now",
        key="monitoring-refresh-now",
        width="stretch",
    )
