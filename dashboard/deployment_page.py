from dataclasses import dataclass

import streamlit as st

from dashboard.formatting import format_dashboard_timestamp
from dashboard.layout import render_component_header
from dashboard.lifecycle import PipelineRun, PodInformation
from dashboard.monitoring import MonitoringState

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


def _status_symbol(status: str) -> str:
    normalized = status.lower()
    if normalized in {
        "healthy",
        "synced",
        "available",
        "correlated",
        "succeeded",
    }:
        return "✓"
    if normalized in {"running", "progressing"}:
        return "▶"
    if normalized in {"degraded", "failed", "error"}:
        return "✕"
    if normalized == "outofsync":
        return "⚠"
    return "—"


def _render_field(label: str, value: object, *, code: bool = False) -> None:
    st.caption(label)
    rendered = _display(value)
    if code and rendered != "Unavailable":
        st.code(rendered, language=None)
    else:
        st.markdown(f"**{rendered}**")


def _render_status_field(label: str, value: object) -> None:
    rendered = _display(value)
    st.caption(label)
    st.markdown(f"**{_status_symbol(rendered)} {rendered}**")


def _render_current_deployment(
    pipeline_run: PipelineRun,
    page_state: DeploymentPageState,
) -> None:
    with st.container(border=True):
        render_component_header("Current Deployment", "LIVE")
        first = st.columns(3, gap="medium")
        with first[0]:
            _render_field("Application", APPLICATION_NAME)
        with first[1]:
            _render_status_field("Overall runtime", page_state.overall_status)
        with first[2]:
            _render_field("Replicas", page_state.replicas)
        second = st.columns(4, gap="medium")
        with second[0]:
            _render_status_field("Argo CD Sync", pipeline_run.argocd.sync_status)
        with second[1]:
            _render_status_field("Health", pipeline_run.argocd.health_status)
        with second[2]:
            _render_field("Namespace", pipeline_run.kubernetes.namespace)
        with second[3]:
            _render_field("Deployment", pipeline_run.kubernetes.deployment)


def _workflow_identity(pipeline_run: PipelineRun) -> str | None:
    run_number = pipeline_run.github.workflow_run_number
    run_id = pipeline_run.workflow_run_id
    if run_number and run_id:
        return f"#{run_number} (ID {run_id})"
    return run_id


def _render_release_identity(
    pipeline_run: PipelineRun,
    page_state: DeploymentPageState,
) -> None:
    with st.container(border=True):
        render_component_header("Release Identity", "LIVE")
        _render_status_field("Artifact correlation", page_state.correlation_status)
        st.caption(
            "Published artifact ≠ desired artifact ≠ deployed artifact ≠ "
            "running artifact. Correlation confirms when their immutable "
            "identities agree."
        )
        left, right = st.columns(2, gap="medium")
        with left:
            _render_field("Commit SHA", pipeline_run.commit_sha, code=True)
            _render_field("Workflow run", _workflow_identity(pipeline_run))
            _render_field("Published GHCR tag", pipeline_run.image_tag, code=True)
            _render_field(
                "Image published",
                format_dashboard_timestamp(pipeline_run.ghcr.published_at),
            )
        with right:
            _render_field("Desired image", page_state.desired_image, code=True)
            _render_field("Running image", page_state.running_image, code=True)
            _render_field("Running image digest", page_state.running_digest, code=True)
            _render_field(
                "Workflow completed",
                format_dashboard_timestamp(pipeline_run.github.completed_at),
            )


def _render_gitops_status(pipeline_run: PipelineRun) -> None:
    argocd = pipeline_run.argocd
    with st.container(border=True):
        render_component_header("GitOps Status", "LIVE")
        _render_field("Application", argocd.application)
        sync, health = st.columns(2, gap="small")
        with sync:
            _render_status_field("Sync status", argocd.sync_status)
        with health:
            _render_status_field("Health status", argocd.health_status)
        _render_field("Target revision", argocd.target_revision, code=True)
        _render_field("Observed revision", argocd.observed_revision, code=True)
        _render_status_field("Latest operation", argocd.operation_phase)
        _render_field(
            "Latest operation timestamp",
            format_dashboard_timestamp(argocd.operation_at),
        )
        st.caption(
            "Synced means the cluster matches Git. Healthy means the current "
            "runtime is operational. Healthy and OutOfSync can occur together."
        )


def _render_pod(pod: PodInformation) -> None:
    with st.container(border=True):
        name, phase, readiness, restarts = st.columns(
            [2, 1, 1, 1],
            gap="small",
        )
        name.markdown(f"**{pod.name}**")
        phase.markdown(_display(pod.phase))
        readiness.markdown("Ready" if pod.ready else "Not ready")
        restarts.markdown(f"{_display(pod.restart_count)} restarts")
        st.caption("Pod created: " + format_dashboard_timestamp(pod.created_at))


def _render_kubernetes_runtime(pipeline_run: PipelineRun) -> None:
    kubernetes = pipeline_run.kubernetes
    with st.container(border=True):
        render_component_header("Kubernetes Runtime", "LIVE")
        identity = st.columns(3, gap="small")
        with identity[0]:
            _render_field("Namespace", kubernetes.namespace)
        with identity[1]:
            _render_field("Deployment", kubernetes.deployment)
        with identity[2]:
            _render_status_field("Rollout", kubernetes.rollout_status)
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
                _render_field(f"{label} replicas", value)
        revisions = st.columns(2, gap="small")
        with revisions[0]:
            _render_field("Deployment revision", kubernetes.deployment_revision)
        with revisions[1]:
            _render_field("ReplicaSet revision", kubernetes.replica_set_revision)
        st.markdown("**Current Pods**")
        if kubernetes.pods:
            for pod in kubernetes.pods:
                _render_pod(pod)
        else:
            st.info("No current Pod information is available.")


def _render_access() -> None:
    with st.container(border=True):
        render_component_header("Access", "LOCAL")
        service = st.columns(3, gap="small")
        with service[0]:
            _render_field("Service", SERVICE_NAME)
        with service[1]:
            _render_field("Type", SERVICE_TYPE)
        with service[2]:
            _render_field("Port", SERVICE_PORT)
        st.caption("Port-forward command (copy from the code block)")
        st.code(PORT_FORWARD_COMMAND, language="powershell")
        st.info(
            "Port-forward exposes the already-running ClusterIP Service. It "
            "does not start or deploy the dashboard, and the local endpoint "
            "is reachable only while a suitable port-forward is active."
        )
        st.link_button("Open Dashboard", LOCAL_ENDPOINT)


def _render_deployment_journey() -> None:
    with st.container(border=True):
        render_component_header("Deployment Journey", "LIVE")
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
    _render_current_deployment(pipeline_run, page_state)
    _render_release_identity(pipeline_run, page_state)
    gitops, runtime = st.columns([1, 1.6], gap="medium")
    with gitops:
        _render_gitops_status(pipeline_run)
    with runtime:
        _render_kubernetes_runtime(pipeline_run)
    access, journey = st.columns(2, gap="medium")
    with access:
        _render_access()
    with journey:
        _render_deployment_journey()
