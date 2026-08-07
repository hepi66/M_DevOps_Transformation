from dataclasses import dataclass

import streamlit as st

from dashboard.formatting import format_dashboard_timestamp
from dashboard.layout import render_component_header
from dashboard.lifecycle import PipelineRun, PodInformation
from dashboard.monitoring import MonitoringState, seconds_until_refresh

APPLICATION_NAME = "m-devops-dashboard"
SERVICE_NAME = "m-devops-dashboard"
SERVICE_TYPE = "ClusterIP"
SERVICE_PORT = 8501
LOCAL_ENDPOINT = "http://127.0.0.1:8501"
PORT_FORWARD_COMMAND = (
    "kubectl port-forward service/m-devops-dashboard 8501:8501 "
    "-n m-devops-dashboard"
)


@dataclass(frozen=True)
class DeploymentPageState:
    """Presentation-ready projection of one normalized monitoring observation."""

    overall_status: str
    replicas: str
    correlation_status: str
    desired_image: str | None
    running_image: str | None
    running_digest: str | None


def _display(value: object) -> str:
    return "Unavailable" if value is None or value == "" else str(value)


def _replica_summary(pipeline_run: PipelineRun) -> str:
    ready = pipeline_run.kubernetes.ready_replicas
    desired = pipeline_run.kubernetes.desired_replicas
    return (
        f"{ready} / {desired} Ready"
        if ready is not None and desired is not None
        else "Unavailable"
    )


def _overall_status(pipeline_run: PipelineRun) -> str:
    kubernetes = pipeline_run.kubernetes
    health = str(pipeline_run.argocd.health_status or "").lower()
    if kubernetes.availability != "available":
        return "Unavailable"
    if kubernetes.status == "failed" or health in {"degraded", "missing"}:
        return "Degraded"
    if kubernetes.status == "running":
        return "Running"
    if kubernetes.status == "completed" and health == "healthy":
        return "Healthy"
    return "Unknown"


def build_deployment_page_state(
    pipeline_run: PipelineRun,
) -> DeploymentPageState:
    """Project existing lifecycle state without retrieving provider data."""
    running_pod = next(
        (pod for pod in pipeline_run.kubernetes.pods if pod.ready),
        pipeline_run.kubernetes.pods[0]
        if pipeline_run.kubernetes.pods
        else None,
    )
    return DeploymentPageState(
        overall_status=_overall_status(pipeline_run),
        replicas=_replica_summary(pipeline_run),
        correlation_status={
            "correlated": "Correlated",
            "partial": "Partially correlated",
            "unknown": "Unknown",
        }[pipeline_run.correlation_status],
        desired_image=pipeline_run.kubernetes.image,
        running_image=running_pod.image if running_pod else None,
        running_digest=(
            running_pod.image_digest
            if running_pod and running_pod.image_digest
            else pipeline_run.kubernetes.image_digest
        ),
    )


def deployment_monitoring_status_text(
    state: MonitoringState,
    *,
    automatic: bool = True,
) -> str:
    """Describe page-level freshness without hiding usable provider data."""
    if not automatic:
        return "Live refresh paused · Manual updates only"
    remaining = seconds_until_refresh(state)
    if state.retrieval_failed:
        return "Refresh failed · Showing the last successful snapshot"

    providers = (
        ("GitHub", state.pipeline_run.github.availability),
        ("GHCR", state.pipeline_run.ghcr.availability),
        ("Argo CD", state.pipeline_run.argocd.availability),
        ("Kubernetes", state.pipeline_run.kubernetes.availability),
    )
    available = [name for name, status in providers if status == "available"]
    if len(available) == len(providers):
        return f"Live deployment data · Next check in {remaining}s"
    if available:
        return (
            "Partial live data · Available: "
            + ", ".join(available)
            + f" · Retry in {remaining}s"
        )
    return f"Deployment data unavailable · Retry in {remaining}s"


def _status_symbol(status: str) -> str:
    normalized = status.lower()
    if normalized in {
        "healthy",
        "synced",
        "available",
        "correlated",
        "succeeded",
        "completed",
        "ready",
        "confirmed",
    }:
        return "✓"
    if normalized in {"running", "progressing", "deploying"}:
        return "▶"
    if normalized in {"degraded", "failed", "unhealthy", "error"}:
        return "✕"
    if normalized in {"outofsync", "partially correlated", "partial"}:
        return "⚠"
    return "—"


def _status_color(status: str) -> str:
    normalized = status.lower()
    if _status_symbol(status) == "✓":
        return "green"
    if normalized in {"running", "progressing", "deploying"}:
        return "blue"
    if normalized in {"outofsync", "partially correlated", "partial"}:
        return "yellow"
    if normalized in {"degraded", "failed", "unhealthy", "error"}:
        return "red"
    return "gray"


def _render_status_badge(status: object, container=st) -> None:
    rendered = _display(status)
    container.badge(
        f"{_status_symbol(rendered)} {rendered}",
        color=_status_color(rendered),
    )


def _render_field(label: str, value: object, *, code: bool = False) -> None:
    st.caption(label)
    rendered = _display(value)
    if code and rendered != "Unavailable":
        st.code(rendered, language=None)
    else:
        st.markdown(f"**{rendered}**")


def _render_status_field(label: str, value: object) -> None:
    st.caption(label)
    _render_status_badge(value)


def _short_release(commit_sha: str | None) -> str:
    return commit_sha[:7] if commit_sha else "Unavailable"


def _render_summary_item(
    label: str,
    value: str,
    *,
    status: str | None = None,
) -> None:
    card = st.container(border=True, height=190)
    card.caption(label)
    card.markdown(f"### {value}")
    if status is not None:
        _render_status_badge(status, card)


def _render_deployment_summary(
    pipeline_run: PipelineRun,
    page_state: DeploymentPageState,
) -> None:
    runtime, gitops, kubernetes, release = st.columns(4, gap="small")
    with runtime:
        _render_summary_item(
            "Runtime",
            page_state.overall_status,
            status=page_state.overall_status,
        )
    with gitops:
        sync_status = _display(pipeline_run.argocd.sync_status)
        _render_summary_item("GitOps", sync_status, status=sync_status)
    with kubernetes:
        kubernetes_status = {
            "completed": "Ready",
            "running": "Running",
            "failed": "Failed",
            "unavailable": "Unavailable",
        }.get(pipeline_run.kubernetes.status, "Unknown")
        _render_summary_item(
            "Kubernetes",
            page_state.replicas,
            status=kubernetes_status,
        )
    with release:
        _render_summary_item(
            "Release",
            _short_release(pipeline_run.commit_sha),
            status=page_state.correlation_status,
        )


def _workflow_identity(pipeline_run: PipelineRun) -> str | None:
    run_number = pipeline_run.github.workflow_run_number
    run_id = pipeline_run.workflow_run_id
    if run_number and run_id:
        return f"#{run_number} (ID {run_id})"
    return run_id


def _stage_evidence(
    pipeline_run: PipelineRun,
    identifier: str,
) -> str:
    stage = pipeline_run.stage(identifier)
    if stage is None:
        return "Unavailable"
    return "Confirmed" if stage.status == "Completed" else stage.status


def _render_evidence_step(label: str, status: str) -> None:
    st.caption(label)
    _render_status_badge(status)


def _render_current_release(
    pipeline_run: PipelineRun,
    page_state: DeploymentPageState,
) -> None:
    with st.container(border=True):
        render_component_header("Current Release", "LIVE")
        release, correlation, published = st.columns(
            [1, 1.2, 1.3],
            gap="medium",
        )
        with release:
            _render_field("Release", _short_release(pipeline_run.commit_sha))
        with correlation:
            _render_status_field(
                "Artifact correlation",
                page_state.correlation_status,
            )
        with published:
            _render_field(
                "Published",
                format_dashboard_timestamp(pipeline_run.ghcr.published_at),
            )

        st.caption("Immutable release evidence")
        evidence_columns = st.columns(4, gap="small")
        evidence = (
            (
                "Git commit",
                "Confirmed" if pipeline_run.commit_sha else "Unavailable",
            ),
            ("GHCR artifact", _stage_evidence(pipeline_run, "ghcr")),
            ("Desired deployment", _stage_evidence(pipeline_run, "argocd")),
            ("Running artifact", _stage_evidence(pipeline_run, "kubernetes")),
        )
        for column, (label, status) in zip(
            evidence_columns,
            evidence,
            strict=True,
        ):
            with column:
                _render_evidence_step(label, status)


def _render_gitops_status(pipeline_run: PipelineRun) -> None:
    argocd = pipeline_run.argocd
    with st.container(border=True, height="stretch"):
        render_component_header("GitOps · Argo CD", "LIVE")
        sync, health = st.columns(2, gap="small")
        with sync:
            _render_status_field("Sync status", argocd.sync_status)
        with health:
            _render_status_field("Health status", argocd.health_status)
        _render_status_field("Latest operation", argocd.operation_phase)
        _render_field(
            "Latest operation",
            format_dashboard_timestamp(argocd.operation_at),
        )
        _render_field("Application", argocd.application)
        st.caption(
            "Synced describes alignment with Git. Healthy describes the "
            "running application; Healthy and OutOfSync may coexist."
        )


def _render_pod(pod: PodInformation) -> None:
    name, phase, readiness, restarts = st.columns(
        [2, 1, 1, 1],
        gap="small",
    )
    name.markdown(f"**{pod.name}**")
    phase.markdown(_display(pod.phase))
    readiness.markdown("✓ Ready" if pod.ready else "— Not ready")
    restarts.markdown(f"{_display(pod.restart_count)} restarts")


def _render_kubernetes_runtime(pipeline_run: PipelineRun) -> None:
    kubernetes = pipeline_run.kubernetes
    with st.container(border=True, height="stretch"):
        render_component_header("Kubernetes Runtime", "LIVE")
        rollout, namespace, deployment = st.columns(
            [1, 1.2, 1.4],
            gap="small",
        )
        with rollout:
            _render_status_field("Rollout", kubernetes.rollout_status)
        with namespace:
            _render_field("Namespace", kubernetes.namespace)
        with deployment:
            _render_field("Deployment", kubernetes.deployment)
        replicas = st.columns(4, gap="small")
        replica_values = (
            kubernetes.desired_replicas,
            kubernetes.updated_replicas,
            kubernetes.ready_replicas,
            kubernetes.available_replicas,
        )
        for column, label, value in zip(
            replicas,
            ("Desired", "Updated", "Ready", "Available"),
            replica_values,
            strict=True,
        ):
            with column:
                _render_field(label, value)
        st.markdown("**Current Pods**")
        if kubernetes.pods:
            for pod in kubernetes.pods:
                _render_pod(pod)
        else:
            st.info("No current Pod information is available.")


def _render_technical_details(
    pipeline_run: PipelineRun,
    page_state: DeploymentPageState,
) -> None:
    with st.expander("Technical Details"):
        release, runtime = st.columns(2, gap="medium")
        with release:
            _render_field("Full commit SHA", pipeline_run.commit_sha, code=True)
            _render_field("Workflow run", _workflow_identity(pipeline_run))
            _render_field("Published GHCR tag", pipeline_run.image_tag, code=True)
            _render_field(
                "Workflow completed",
                format_dashboard_timestamp(pipeline_run.github.completed_at),
            )
            _render_field(
                "Image published",
                format_dashboard_timestamp(pipeline_run.ghcr.published_at),
            )
            _render_field(
                "Target revision",
                pipeline_run.argocd.target_revision,
                code=True,
            )
            _render_field(
                "Observed revision",
                pipeline_run.argocd.observed_revision,
                code=True,
            )
        with runtime:
            _render_field("Desired image", page_state.desired_image, code=True)
            _render_field("Running image", page_state.running_image, code=True)
            _render_field(
                "Running image digest",
                page_state.running_digest,
                code=True,
            )
            _render_field(
                "Deployment revision",
                pipeline_run.kubernetes.deployment_revision,
            )
            _render_field(
                "ReplicaSet revision",
                pipeline_run.kubernetes.replica_set_revision,
            )
            if pipeline_run.kubernetes.pods:
                _render_field(
                    "Pod created",
                    format_dashboard_timestamp(
                        pipeline_run.kubernetes.pods[0].created_at
                    ),
                )


def _render_access() -> None:
    with st.container(border=True):
        render_component_header("Access", "LOCAL")
        service = st.columns(4, gap="small")
        values = (
            ("Service", SERVICE_NAME),
            ("Type", SERVICE_TYPE),
            ("Port", SERVICE_PORT),
            ("Local access", LOCAL_ENDPOINT),
        )
        for column, (label, value) in zip(service, values, strict=True):
            with column:
                _render_field(label, value)
        st.caption("Port-forward command")
        st.code(PORT_FORWARD_COMMAND, language="powershell")
        st.info(
            "Port-forward exposes the already-running ClusterIP Service. It "
            "does not start or deploy the dashboard. Open Dashboard works "
            "only while a suitable port-forward is active."
        )
        st.link_button("Open Dashboard", LOCAL_ENDPOINT)


def _render_deployment_journey() -> None:
    with st.expander("Deployment Journey"):
        st.markdown(
            "**GitHub Actions** → **GHCR** → **Immutable SHA Promotion** → "
            "**Argo CD** → **Kubernetes Deployment** → **ReplicaSet** → "
            "**Pod** → **Service** → **Dashboard**"
        )
        st.caption(
            "Image publication creates an artifact. Deployment begins only "
            "after the immutable SHA is promoted in Git and the child Argo CD "
            "Application is explicitly synchronized."
        )


def render_deployment_page(monitoring_state: MonitoringState) -> None:
    """Render the detailed deployment page from one shared monitoring state."""
    pipeline_run = monitoring_state.pipeline_run
    page_state = build_deployment_page_state(pipeline_run)
    st.caption(
        "Monitoring snapshot: "
        + format_dashboard_timestamp(monitoring_state.last_success)
    )
    _render_deployment_summary(pipeline_run, page_state)
    _render_current_release(pipeline_run, page_state)
    gitops, runtime = st.columns([1, 1.35], gap="medium")
    with gitops:
        _render_gitops_status(pipeline_run)
    with runtime:
        _render_kubernetes_runtime(pipeline_run)
    _render_technical_details(pipeline_run, page_state)
    _render_access()
    _render_deployment_journey()
