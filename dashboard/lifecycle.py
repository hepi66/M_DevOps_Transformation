from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

ProviderAvailability = Literal[
    "available",
    "missing",
    "unavailable",
    "authentication_unavailable",
    "unknown",
]
LifecycleStatus = Literal[
    "completed",
    "running",
    "queued",
    "failed",
    "cancelled",
    "unavailable",
    "unknown",
]
RefreshStatus = Literal["success", "partial", "unavailable"]
CorrelationStatus = Literal["correlated", "partial", "unknown"]


@dataclass(frozen=True)
class WorkflowStep:
    """Normalized GitHub Actions step."""

    name: str
    status: str | None = None
    conclusion: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass(frozen=True)
class WorkflowJob:
    """Normalized GitHub Actions job and its complete step hierarchy."""

    name: str
    status: str | None = None
    conclusion: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    steps: tuple[WorkflowStep, ...] = ()


@dataclass(frozen=True)
class GitHubProviderData:
    """Normalized repository and GitHub Actions observation."""

    availability: ProviderAvailability
    repository: str | None = None
    repository_url: str | None = None
    branch: str | None = None
    status: LifecycleStatus = "unknown"
    workflow_name: str | None = None
    workflow_run_id: str | None = None
    workflow_run_number: int | None = None
    workflow_url: str | None = None
    commit_sha: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    jobs: tuple[WorkflowJob, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class GHCRProviderData:
    """Normalized GitHub Container Registry observation."""

    availability: ProviderAvailability
    status: LifecycleStatus
    package_name: str | None = None
    image_name: str | None = None
    tags: tuple[str, ...] = ()
    latest_tag: str | None = None
    digest: str | None = None
    published_at: datetime | None = None
    package_url: str | None = None
    visibility: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class ArgoCDProviderData:
    """Normalized Argo CD observation when provider data is present."""

    availability: ProviderAvailability
    status: LifecycleStatus
    application: str | None = None
    target_revision: str | None = None
    observed_revision: str | None = None
    namespace: str | None = None
    sync_status: str | None = None
    health_status: str | None = None
    operation_phase: str | None = None
    observed_at: datetime | None = None
    workflow_run_id: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class PodInformation:
    """Normalized Kubernetes Pod observation."""

    name: str
    phase: str | None = None
    ready: bool | None = None
    restart_count: int | None = None
    image: str | None = None
    image_digest: str | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class KubernetesProviderData:
    """Normalized Kubernetes workload observation when provider data is present."""

    availability: ProviderAvailability
    status: LifecycleStatus
    namespace: str | None = None
    deployment: str | None = None
    deployment_revision: str | None = None
    image_tag: str | None = None
    image_digest: str | None = None
    available_replicas: int | None = None
    desired_replicas: int | None = None
    updated_replicas: int | None = None
    ready_replicas: int | None = None
    observed_generation: int | None = None
    rollout_status: str | None = None
    replica_set_revision: str | None = None
    pods: tuple[PodInformation, ...] = ()
    observed_at: datetime | None = None
    workflow_run_id: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class PipelineStageState:
    """Provider-independent state mapped to one established pipeline stage."""

    identifier: str
    status: str
    source_classification: Literal["DEMO", "LOCAL", "LIVE"]
    timestamp: datetime | None = None
    details: str | None = None


@dataclass(frozen=True)
class PipelineRun:
    """One correlated observation of the software delivery lifecycle."""

    commit_sha: str | None
    workflow_run_id: str | None
    branch: str | None
    workflow_status: LifecycleStatus
    current_stage: str | None
    completed_stages: tuple[str, ...]
    failed_stage: str | None
    image_tag: str | None
    image_digest: str | None
    deployment_revision: str | None
    deployment_namespace: str | None
    pod_information: tuple[PodInformation, ...]
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: int | None
    last_refresh: datetime | None
    refresh_interval_seconds: int
    refresh_status: RefreshStatus
    next_refresh: datetime | None
    correlation_status: CorrelationStatus
    stages: tuple[PipelineStageState, ...]
    github: GitHubProviderData
    ghcr: GHCRProviderData
    argocd: ArgoCDProviderData
    kubernetes: KubernetesProviderData

    def stage(self, identifier: str) -> PipelineStageState | None:
        """Return a mapped stage without exposing provider-specific structures."""
        return next(
            (stage for stage in self.stages if stage.identifier == identifier),
            None,
        )


def parse_provider_timestamp(value: object) -> datetime | None:
    """Normalize provider timestamps to timezone-aware datetime values."""
    if isinstance(value, datetime):
        return (
            value.replace(tzinfo=timezone.utc)
            if value.tzinfo is None
            else value
        )
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (
        parsed.replace(tzinfo=timezone.utc)
        if parsed.tzinfo is None
        else parsed
    )


def _availability(value: object) -> ProviderAvailability:
    normalized = str(value or "unknown").lower()
    if normalized in {
        "available",
        "missing",
        "unavailable",
        "authentication_unavailable",
    }:
        return normalized  # type: ignore[return-value]
    return "unknown"


def _workflow_status(status: object, conclusion: object) -> LifecycleStatus:
    raw_status = str(status or "").lower()
    raw_conclusion = str(conclusion or "").lower()
    if raw_status in {"queued", "requested", "waiting", "pending", "expected"}:
        return "queued"
    if raw_status == "in_progress":
        return "running"
    if raw_conclusion in {"failure", "timed_out", "startup_failure", "action_required"}:
        return "failed"
    if raw_conclusion == "cancelled":
        return "cancelled"
    if raw_status == "completed" and raw_conclusion in {"success", "neutral", "skipped"}:
        return "completed"
    return "unknown"


def _normalize_step(step: dict[str, Any]) -> WorkflowStep:
    return WorkflowStep(
        name=str(step.get("name") or "Unnamed step"),
        status=step.get("status"),
        conclusion=step.get("conclusion"),
        started_at=parse_provider_timestamp(step.get("startedAt")),
        completed_at=parse_provider_timestamp(step.get("completedAt")),
    )


def _normalize_job(job: dict[str, Any]) -> WorkflowJob:
    return WorkflowJob(
        name=str(job.get("name") or "Unnamed job"),
        status=job.get("status"),
        conclusion=job.get("conclusion"),
        started_at=parse_provider_timestamp(job.get("startedAt")),
        completed_at=parse_provider_timestamp(job.get("completedAt")),
        steps=tuple(
            _normalize_step(step)
            for step in (job.get("steps") or ())
            if isinstance(step, dict)
        ),
    )


def normalize_github_provider(snapshot: dict[str, Any]) -> GitHubProviderData:
    """Normalize the existing GitHub snapshot without performing retrieval."""
    actions = snapshot.get("github_actions")
    actions = actions if isinstance(actions, dict) else {}
    workflow = actions.get("workflow")
    workflow = workflow if isinstance(workflow, dict) else {}
    jobs = actions.get("jobs")
    jobs = jobs if isinstance(jobs, list) else []

    availability = _availability(actions.get("availability"))
    state = str(snapshot.get("state") or "").lower()
    status = _workflow_status(workflow.get("status"), workflow.get("conclusion"))
    if status == "unknown":
        status = {
            "healthy": "completed",
            "running": "running",
            "attention required": "failed",
            "not available": "unavailable",
        }.get(state, "unknown")

    run_id = workflow.get("databaseId")
    run_number = workflow.get("number")
    return GitHubProviderData(
        availability=availability,
        repository=snapshot.get("repository"),
        repository_url=snapshot.get("repository_url"),
        branch=workflow.get("headBranch") or snapshot.get("branch"),
        status=status,
        workflow_name=workflow.get("name"),
        workflow_run_id=str(run_id) if run_id is not None else None,
        workflow_run_number=run_number if isinstance(run_number, int) else None,
        workflow_url=workflow.get("url"),
        commit_sha=workflow.get("headSha"),
        created_at=parse_provider_timestamp(workflow.get("createdAt")),
        started_at=parse_provider_timestamp(workflow.get("startedAt")),
        completed_at=parse_provider_timestamp(workflow.get("updatedAt")),
        jobs=tuple(_normalize_job(job) for job in jobs if isinstance(job, dict)),
        reason=actions.get("reason") or snapshot.get("reason"),
    )


def normalize_ghcr_provider(snapshot: dict[str, Any]) -> GHCRProviderData:
    """Normalize the existing GHCR snapshot without performing retrieval."""
    raw = snapshot.get("ghcr")
    raw = raw if isinstance(raw, dict) else {}
    availability = _availability(raw.get("availability"))
    status: LifecycleStatus = (
        "completed"
        if availability == "available"
        else "unavailable"
        if availability in {
            "missing",
            "unavailable",
            "authentication_unavailable",
        }
        else "unknown"
    )
    raw_tags = raw.get("tags")
    tags = (
        tuple(str(tag) for tag in raw_tags if tag)
        if isinstance(raw_tags, (list, tuple))
        else ()
    )
    latest_tag = raw.get("latest_tag")
    if latest_tag and str(latest_tag) not in tags:
        tags = (*tags, str(latest_tag))
    return GHCRProviderData(
        availability=availability,
        status=status,
        package_name=raw.get("package_name"),
        image_name=raw.get("image_name"),
        tags=tags,
        latest_tag=str(latest_tag) if latest_tag else None,
        digest=raw.get("digest"),
        published_at=parse_provider_timestamp(raw.get("published_at")),
        package_url=raw.get("package_url"),
        visibility=raw.get("visibility"),
        reason=raw.get("reason"),
    )


def normalize_argocd_provider(snapshot: dict[str, Any]) -> ArgoCDProviderData:
    """Normalize optional Argo CD data; unknown means no provider exists yet."""
    raw = snapshot.get("argocd")
    raw = raw if isinstance(raw, dict) else {}
    availability = _availability(raw.get("availability"))
    sync_status = raw.get("sync_status") or raw.get("syncStatus")
    health_status = raw.get("health_status") or raw.get("healthStatus")
    if str(health_status).lower() in {"degraded", "missing"}:
        status: LifecycleStatus = "failed"
    elif (
        str(sync_status).lower() == "synced"
        and str(health_status).lower() == "healthy"
    ):
        status = "completed"
    elif str(health_status).lower() in {"progressing", "suspended"}:
        status = "running"
    else:
        status = "unknown" if availability == "unknown" else "unavailable"
    return ArgoCDProviderData(
        availability=availability,
        status=status,
        application=raw.get("application"),
        target_revision=raw.get("target_revision"),
        observed_revision=raw.get("observed_revision") or raw.get("revision"),
        namespace=raw.get("namespace"),
        sync_status=sync_status,
        health_status=health_status,
        operation_phase=raw.get("operation_phase"),
        observed_at=parse_provider_timestamp(raw.get("observed_at")),
        workflow_run_id=(
            str(raw["workflow_run_id"])
            if raw.get("workflow_run_id") is not None
            else None
        ),
        reason=raw.get("reason"),
    )


def normalize_kubernetes_provider(
    snapshot: dict[str, Any],
) -> KubernetesProviderData:
    """Normalize optional Kubernetes data; unknown means no provider exists yet."""
    raw = snapshot.get("kubernetes")
    raw = raw if isinstance(raw, dict) else {}
    availability = _availability(raw.get("availability"))
    raw_pods = raw.get("pods")
    pods = tuple(
        PodInformation(
            name=str(pod.get("name") or "Unnamed pod"),
            phase=pod.get("phase"),
            ready=pod.get("ready") if isinstance(pod.get("ready"), bool) else None,
            restart_count=(
                pod.get("restart_count")
                if isinstance(pod.get("restart_count"), int)
                else None
            ),
            image=pod.get("image"),
            image_digest=pod.get("image_digest"),
            created_at=parse_provider_timestamp(pod.get("created_at")),
        )
        for pod in (raw_pods if isinstance(raw_pods, list) else ())
        if isinstance(pod, dict)
    )
    desired = raw.get("desired_replicas")
    available = raw.get("available_replicas")
    if raw.get("failed"):
        status: LifecycleStatus = "failed"
    elif (
        isinstance(desired, int)
        and isinstance(available, int)
        and desired > 0
        and available >= desired
    ):
        status = "completed"
    elif availability == "available":
        status = "running"
    else:
        status = "unknown" if availability == "unknown" else "unavailable"
    return KubernetesProviderData(
        availability=availability,
        status=status,
        namespace=raw.get("namespace"),
        deployment=raw.get("deployment"),
        deployment_revision=raw.get("deployment_revision") or raw.get("revision"),
        image_tag=raw.get("image_tag"),
        image_digest=raw.get("image_digest"),
        available_replicas=available if isinstance(available, int) else None,
        desired_replicas=desired if isinstance(desired, int) else None,
        updated_replicas=(
            raw.get("updated_replicas")
            if isinstance(raw.get("updated_replicas"), int)
            else None
        ),
        ready_replicas=(
            raw.get("ready_replicas")
            if isinstance(raw.get("ready_replicas"), int)
            else None
        ),
        observed_generation=(
            raw.get("observed_generation")
            if isinstance(raw.get("observed_generation"), int)
            else None
        ),
        rollout_status=raw.get("rollout_status"),
        replica_set_revision=raw.get("replica_set_revision"),
        pods=pods,
        observed_at=parse_provider_timestamp(raw.get("observed_at")),
        workflow_run_id=(
            str(raw["workflow_run_id"])
            if raw.get("workflow_run_id") is not None
            else None
        ),
        reason=raw.get("reason"),
    )


def _docker_stage(snapshot: dict[str, Any]) -> PipelineStageState:
    raw = snapshot.get("docker_build")
    if not isinstance(raw, dict) or raw.get("availability") != "available":
        return PipelineStageState("build", "Unknown", "LIVE")
    job = raw.get("job")
    step = raw.get("step")
    if not isinstance(job, dict) or not isinstance(step, dict):
        return PipelineStageState("build", "Unknown", "LIVE")
    status = _workflow_status(step.get("status"), step.get("conclusion"))
    if status == "unknown":
        status = _workflow_status(job.get("status"), job.get("conclusion"))
    label = {
        "completed": "Completed",
        "running": "Active",
        "queued": "Active",
        "failed": "Failed",
        "cancelled": "Failed",
    }.get(status, "Unknown")
    return PipelineStageState(
        "build",
        label,
        "LIVE",
        parse_provider_timestamp(
            step.get("completedAt")
            or step.get("startedAt")
            or job.get("completedAt")
            or job.get("startedAt")
        ),
        step.get("name") or "Build and push",
    )


def _stage_mapping(
    snapshot: dict[str, Any],
    github: GitHubProviderData,
    ghcr: GHCRProviderData,
    argocd: ArgoCDProviderData,
    kubernetes: KubernetesProviderData,
    *,
    run_detected: bool,
    github_evidence: bool,
    image_correlated: bool,
    deployment_correlated: bool,
    runtime_correlated: bool,
) -> tuple[PipelineStageState, ...]:
    if not run_detected:
        return tuple(
            PipelineStageState(
                identifier,
                "Unknown",
                source,
            )
            for identifier, source in (
                ("code", "LOCAL"),
                ("github", "LIVE"),
                ("ci", "LIVE"),
                ("build", "LIVE"),
                ("ghcr", "LIVE"),
                ("argocd", "LIVE"),
                ("kubernetes", "LIVE"),
            )
        )

    ci_status = (
        {
            "completed": "Success",
            "running": "Running",
            "queued": "Queued",
            "failed": "Failed",
            "cancelled": "Cancelled",
        }.get(github.status, "Unknown")
        if github_evidence
        else "Unknown"
    )
    ghcr_status = (
        "Image published"
        if image_correlated
        else "Failed"
        if ghcr.status == "failed"
        else "Unknown"
    )

    argocd_stage = PipelineStageState("argocd", "Unknown", "LIVE")
    if deployment_correlated:
        argocd_stage = PipelineStageState(
            "argocd",
            {
                "completed": "Completed",
                "running": "Active",
                "failed": "Failed",
            }.get(argocd.status, "Unknown"),
            "LIVE",
            argocd.observed_at,
            argocd.application,
        )

    kubernetes_stage = PipelineStageState("kubernetes", "Unknown", "LIVE")
    if runtime_correlated:
        kubernetes_stage = PipelineStageState(
            "kubernetes",
            {
                "completed": "Completed",
                "running": "Active",
                "failed": "Failed",
            }.get(kubernetes.status, "Unknown"),
            "LIVE",
            kubernetes.observed_at,
            kubernetes.deployment,
        )

    return (
        PipelineStageState("code", "Completed", "LOCAL"),
        PipelineStageState(
            "github",
            "Completed" if github_evidence else "Unknown",
            "LIVE",
            github.completed_at,
            github.repository,
        ),
        PipelineStageState(
            "ci",
            ci_status,
            "LIVE",
            github.completed_at or github.started_at or github.created_at,
            (
                f"Run #{github.workflow_run_number} · {github.branch}"
                if github.workflow_run_number is not None and github.branch
                else None
            ),
        ),
        _docker_stage(snapshot),
        PipelineStageState(
            "ghcr",
            ghcr_status,
            "LIVE",
            ghcr.published_at,
            ghcr.image_name or ghcr.reason,
        ),
        argocd_stage,
        kubernetes_stage,
    )


def _tag_matches_commit(tag: str, commit_sha: str) -> bool:
    return tag == commit_sha or (
        len(tag) >= 7 and commit_sha.startswith(tag)
    )


def _commit_from_image_tag(image_tag: str | None) -> str | None:
    if not image_tag:
        return None
    normalized = image_tag.lower()
    if len(normalized) < 7 or len(normalized) > 40:
        return None
    if any(character not in "0123456789abcdef" for character in normalized):
        return None
    return normalized


def aggregate_pipeline_run(
    snapshot: dict[str, Any],
    *,
    argocd_observation: ArgoCDProviderData | None = None,
    kubernetes_observation: KubernetesProviderData | None = None,
    refresh_interval_seconds: int = 60,
) -> PipelineRun:
    """Normalize and correlate one authoritative runtime snapshot."""
    github = normalize_github_provider(snapshot)
    ghcr = normalize_ghcr_provider(snapshot)
    argocd = argocd_observation or normalize_argocd_provider(snapshot)
    kubernetes = (
        kubernetes_observation
        or normalize_kubernetes_provider(snapshot)
    )

    commit_sha = github.commit_sha or _commit_from_image_tag(
        kubernetes.image_tag
    )
    run_detected = bool(commit_sha)
    github_evidence = bool(
        github.commit_sha and github.workflow_run_id
    )
    image_correlated = bool(
        commit_sha
        and any(_tag_matches_commit(tag, commit_sha) for tag in ghcr.tags)
    )
    image_tag = (
        next(
            (tag for tag in ghcr.tags if _tag_matches_commit(tag, commit_sha or "")),
            None,
        )
        if image_correlated
        else None
    )
    deployment_correlated = bool(
        commit_sha
        and argocd.observed_revision
        and (
            argocd.observed_revision == commit_sha
            or commit_sha.startswith(argocd.observed_revision)
            or argocd.observed_revision.startswith(commit_sha)
        )
    )
    runtime_correlated = bool(
        kubernetes.availability == "available"
        and kubernetes.image_tag
        and commit_sha
        and _tag_matches_commit(kubernetes.image_tag, commit_sha)
    )
    stages = _stage_mapping(
        snapshot,
        github,
        ghcr,
        argocd,
        kubernetes,
        run_detected=run_detected,
        github_evidence=github_evidence,
        image_correlated=image_correlated,
        deployment_correlated=deployment_correlated,
        runtime_correlated=runtime_correlated,
    )

    failed_stage = next(
        (
            stage.identifier
            for stage in stages
            if stage.status in {"Failed", "Authentication unavailable"}
        ),
        None,
    )
    completed_stages = tuple(
        stage.identifier
        for stage in stages
        if stage.status in {"Completed", "Success", "Image published"}
    )
    active_stage = next(
        (
            stage.identifier
            for stage in stages
            if stage.status in {"Active", "Running", "Queued"}
        ),
        None,
    )
    current_stage = failed_stage or active_stage or (
        completed_stages[-1] if completed_stages else None
    )

    started_at = github.started_at or github.created_at
    completed_at = github.completed_at if github.status == "completed" else None
    duration_seconds = (
        max(0, int((completed_at - started_at).total_seconds()))
        if started_at and completed_at
        else None
    )
    last_refresh = parse_provider_timestamp(snapshot.get("refreshed_at"))
    next_refresh = (
        last_refresh + timedelta(seconds=refresh_interval_seconds)
        if last_refresh
        else None
    )
    available_count = sum(
        provider.availability == "available"
        for provider in (github, ghcr, argocd, kubernetes)
    )
    refresh_status: RefreshStatus = (
        "success"
        if available_count == 4
        else "partial"
        if available_count
        else "unavailable"
    )
    correlation_status: CorrelationStatus = (
        "correlated"
        if image_correlated and deployment_correlated and runtime_correlated
        else "partial"
        if image_correlated or deployment_correlated or runtime_correlated
        else "unknown"
    )

    return PipelineRun(
        commit_sha=commit_sha,
        workflow_run_id=github.workflow_run_id,
        branch=github.branch,
        workflow_status=github.status,
        current_stage=current_stage,
        completed_stages=completed_stages,
        failed_stage=failed_stage,
        image_tag=image_tag,
        image_digest=ghcr.digest if image_correlated else None,
        deployment_revision=(
            argocd.observed_revision
            if deployment_correlated
            else None
        ),
        deployment_namespace=(
            kubernetes.namespace
            if runtime_correlated
            else argocd.namespace
            if deployment_correlated
            else None
        ),
        pod_information=kubernetes.pods if runtime_correlated else (),
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=duration_seconds,
        last_refresh=last_refresh,
        refresh_interval_seconds=refresh_interval_seconds,
        refresh_status=refresh_status,
        next_refresh=next_refresh,
        correlation_status=correlation_status,
        stages=stages,
        github=github,
        ghcr=ghcr,
        argocd=argocd,
        kubernetes=kubernetes,
    )
