import os
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from dashboard.lifecycle import (
    ArgoCDProviderData,
    KubernetesProviderData,
    PodInformation,
    parse_provider_timestamp,
)

SERVICE_ACCOUNT_DIRECTORY = Path("/var/run/secrets/kubernetes.io/serviceaccount")
DEFAULT_DASHBOARD_NAMESPACE = "m-devops-dashboard"
DEFAULT_DASHBOARD_DEPLOYMENT = "m-devops-dashboard"
DEFAULT_ARGOCD_NAMESPACE = "argocd"
DEFAULT_ARGOCD_APPLICATION = "m-devops-dashboard"
WORKLOAD_LABEL_SELECTOR = (
    "app.kubernetes.io/name=m-devops-dashboard,"
    "app.kubernetes.io/instance=m-devops-dashboard"
)


@dataclass(frozen=True)
class KubernetesAPIConfiguration:
    """In-cluster Kubernetes API connection details."""

    base_url: str
    token: str
    certificate_authority: Path
    dashboard_namespace: str
    dashboard_deployment: str
    argocd_namespace: str
    argocd_application: str


class KubernetesAPI:
    """Minimal read-only Kubernetes API client."""

    def __init__(
        self,
        configuration: KubernetesAPIConfiguration,
        *,
        session: requests.Session | None = None,
    ) -> None:
        self.configuration = configuration
        self.session = session or requests.Session()

    def get(self, path: str) -> dict[str, Any]:
        """Retrieve one Kubernetes resource without exposing credentials."""
        response = self.session.get(
            f"{self.configuration.base_url}{path}",
            headers={
                "Authorization": f"Bearer {self.configuration.token}",
                "Accept": "application/json",
            },
            verify=str(self.configuration.certificate_authority),
            timeout=5,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise TypeError("Kubernetes API returned an unexpected response.")
        return payload


def load_in_cluster_configuration(
    environ: Mapping[str, str] | None = None,
    *,
    service_account_directory: Path = SERVICE_ACCOUNT_DIRECTORY,
) -> KubernetesAPIConfiguration | None:
    """Load automatic Pod credentials or return a safe local fallback."""
    environment = environ if environ is not None else os.environ
    host = environment.get("KUBERNETES_SERVICE_HOST")
    port = environment.get("KUBERNETES_SERVICE_PORT_HTTPS", "443")
    token_path = service_account_directory / "token"
    ca_path = service_account_directory / "ca.crt"
    namespace_path = service_account_directory / "namespace"
    if (
        not host
        or not token_path.is_file()
        or not ca_path.is_file()
        or not namespace_path.is_file()
    ):
        return None

    token = token_path.read_text(encoding="utf-8").strip()
    mounted_namespace = namespace_path.read_text(encoding="utf-8").strip()
    if not token or not mounted_namespace:
        return None

    return KubernetesAPIConfiguration(
        base_url=f"https://{host}:{port}",
        token=token,
        certificate_authority=ca_path,
        dashboard_namespace=environment.get(
            "DASHBOARD_NAMESPACE",
            mounted_namespace,
        ),
        dashboard_deployment=environment.get(
            "DASHBOARD_DEPLOYMENT",
            DEFAULT_DASHBOARD_DEPLOYMENT,
        ),
        argocd_namespace=environment.get(
            "ARGOCD_NAMESPACE",
            DEFAULT_ARGOCD_NAMESPACE,
        ),
        argocd_application=environment.get(
            "ARGOCD_APPLICATION",
            DEFAULT_ARGOCD_APPLICATION,
        ),
    )


def _unavailable_argocd(reason: str) -> ArgoCDProviderData:
    return ArgoCDProviderData(
        availability="unavailable",
        status="unavailable",
        reason=reason,
    )


def _unavailable_kubernetes(reason: str) -> KubernetesProviderData:
    return KubernetesProviderData(
        availability="unavailable",
        status="unavailable",
        reason=reason,
    )


def observe_argocd(
    api: KubernetesAPI | None,
) -> ArgoCDProviderData:
    """Read and normalize the dashboard Argo CD Application."""
    if api is None:
        return _unavailable_argocd(
            "In-cluster Kubernetes configuration is not available."
        )
    configuration = api.configuration
    path = (
        "/apis/argoproj.io/v1alpha1/namespaces/"
        f"{quote(configuration.argocd_namespace, safe='')}/applications/"
        f"{quote(configuration.argocd_application, safe='')}"
    )
    try:
        application = api.get(path)
    except (requests.RequestException, TypeError) as error:
        return _unavailable_argocd(
            f"Argo CD Application retrieval failed: {type(error).__name__}."
        )

    metadata = application.get("metadata") or {}
    spec = application.get("spec") or {}
    source = spec.get("source") or {}
    destination = spec.get("destination") or {}
    status = application.get("status") or {}
    sync = status.get("sync") or {}
    health = status.get("health") or {}
    operation = status.get("operationState") or {}
    sync_status = sync.get("status")
    health_status = health.get("status")
    if str(health_status).lower() in {"degraded", "missing"}:
        lifecycle_status = "failed"
    elif (
        str(sync_status).lower() == "synced"
        and str(health_status).lower() == "healthy"
    ):
        lifecycle_status = "completed"
    elif (
        str(health_status).lower() == "progressing"
        or str(operation.get("phase")).lower() in {"running", "terminating"}
    ):
        lifecycle_status = "running"
    else:
        lifecycle_status = "unknown"

    return ArgoCDProviderData(
        availability="available",
        status=lifecycle_status,
        application=metadata.get("name"),
        target_revision=source.get("targetRevision"),
        observed_revision=sync.get("revision"),
        namespace=destination.get("namespace"),
        sync_status=sync_status,
        health_status=health_status,
        operation_phase=operation.get("phase"),
        operation_at=parse_provider_timestamp(
            operation.get("finishedAt") or operation.get("startedAt")
        ),
        observed_at=parse_provider_timestamp(
            status.get("reconciledAt")
            or operation.get("finishedAt")
            or operation.get("startedAt")
        ),
    )


def _image_identity(image: str | None) -> tuple[str | None, str | None]:
    if not image:
        return None, None
    if "@" in image:
        _, digest = image.rsplit("@", 1)
        return None, digest
    final_segment = image.rsplit("/", 1)[-1]
    if ":" not in final_segment:
        return None, None
    return final_segment.rsplit(":", 1)[-1], None


def _pod_information(pod: dict[str, Any]) -> PodInformation:
    metadata = pod.get("metadata") or {}
    status = pod.get("status") or {}
    specifications = pod.get("spec") or {}
    containers = specifications.get("containers") or []
    container_statuses = status.get("containerStatuses") or []
    ready_condition = next(
        (
            condition
            for condition in (status.get("conditions") or [])
            if condition.get("type") == "Ready"
        ),
        {},
    )
    image = containers[0].get("image") if containers else None
    image_id = (
        container_statuses[0].get("imageID")
        if container_statuses
        else None
    )
    _, image_digest = _image_identity(image_id)
    return PodInformation(
        name=str(metadata.get("name") or "Unnamed pod"),
        phase=status.get("phase"),
        ready=str(ready_condition.get("status")).lower() == "true",
        restart_count=sum(
            int(container.get("restartCount") or 0)
            for container in container_statuses
        ),
        image=image,
        image_digest=image_digest,
        created_at=parse_provider_timestamp(metadata.get("creationTimestamp")),
    )


def observe_kubernetes(
    api: KubernetesAPI | None,
) -> KubernetesProviderData:
    """Read and normalize the dashboard Deployment, ReplicaSets, and Pods."""
    if api is None:
        return _unavailable_kubernetes(
            "In-cluster Kubernetes configuration is not available."
        )
    configuration = api.configuration
    namespace = quote(configuration.dashboard_namespace, safe="")
    deployment_name = quote(configuration.dashboard_deployment, safe="")
    selector = quote(WORKLOAD_LABEL_SELECTOR, safe="")
    try:
        deployment = api.get(
            f"/apis/apps/v1/namespaces/{namespace}/deployments/"
            f"{deployment_name}"
        )
        replica_sets = api.get(
            f"/apis/apps/v1/namespaces/{namespace}/replicasets"
            f"?labelSelector={selector}"
        )
        pods_payload = api.get(
            f"/api/v1/namespaces/{namespace}/pods"
            f"?labelSelector={selector}"
        )
    except (requests.RequestException, TypeError) as error:
        return _unavailable_kubernetes(
            f"Kubernetes workload retrieval failed: {type(error).__name__}."
        )

    metadata = deployment.get("metadata") or {}
    spec = deployment.get("spec") or {}
    status = deployment.get("status") or {}
    template = spec.get("template") or {}
    pod_spec = template.get("spec") or {}
    containers = pod_spec.get("containers") or []
    image = containers[0].get("image") if containers else None
    image_tag, declared_digest = _image_identity(image)
    pods = tuple(
        _pod_information(pod)
        for pod in (pods_payload.get("items") or [])
        if isinstance(pod, dict)
    )
    running_digest = next(
        (pod.image_digest for pod in pods if pod.image_digest),
        declared_digest,
    )

    desired = spec.get("replicas")
    available = status.get("availableReplicas", 0)
    updated = status.get("updatedReplicas", 0)
    ready = status.get("readyReplicas", 0)
    failed = any(
        condition.get("type") == "Progressing"
        and str(condition.get("status")).lower() == "false"
        for condition in (status.get("conditions") or [])
    )
    if failed:
        lifecycle_status = "failed"
        rollout_status = "Failed"
    elif (
        isinstance(desired, int)
        and desired > 0
        and available >= desired
        and updated >= desired
        and ready >= desired
    ):
        lifecycle_status = "completed"
        rollout_status = "Available"
    else:
        lifecycle_status = "running"
        rollout_status = "Progressing"

    replica_set_items = [
        item
        for item in (replica_sets.get("items") or [])
        if isinstance(item, dict)
    ]
    replica_set_revisions = [
        str(
            (item.get("metadata") or {})
            .get("annotations", {})
            .get("deployment.kubernetes.io/revision")
        )
        for item in replica_set_items
        if (
            (item.get("metadata") or {})
            .get("annotations", {})
            .get("deployment.kubernetes.io/revision")
        )
    ]
    replica_set_revision = max(
        replica_set_revisions,
        key=lambda value: int(value) if value.isdigit() else -1,
        default=None,
    )

    return KubernetesProviderData(
        availability="available",
        status=lifecycle_status,
        namespace=configuration.dashboard_namespace,
        deployment=metadata.get("name"),
        deployment_revision=(
            (metadata.get("annotations") or {}).get(
                "deployment.kubernetes.io/revision"
            )
        ),
        image=image,
        image_tag=image_tag,
        image_digest=running_digest,
        available_replicas=available if isinstance(available, int) else None,
        desired_replicas=desired if isinstance(desired, int) else None,
        updated_replicas=updated if isinstance(updated, int) else None,
        ready_replicas=ready if isinstance(ready, int) else None,
        observed_generation=(
            status.get("observedGeneration")
            if isinstance(status.get("observedGeneration"), int)
            else None
        ),
        rollout_status=rollout_status,
        replica_set_revision=replica_set_revision,
        pods=pods,
        observed_at=max(
            (pod.created_at for pod in pods if pod.created_at),
            default=None,
        ),
    )


def load_cluster_observations() -> tuple[
    ArgoCDProviderData,
    KubernetesProviderData,
]:
    """Retrieve both in-cluster observations through one API configuration."""
    configuration = load_in_cluster_configuration()
    api = KubernetesAPI(configuration) if configuration else None
    return observe_argocd(api), observe_kubernetes(api)


def provider_snapshot(
    argocd: ArgoCDProviderData,
    kubernetes: KubernetesProviderData,
) -> dict[str, dict[str, Any]]:
    """Adapt normalized providers for the established event renderer."""
    return {
        "argocd": asdict(argocd),
        "kubernetes": asdict(kubernetes),
    }
