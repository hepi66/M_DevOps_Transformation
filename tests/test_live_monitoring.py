from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import requests

from dashboard import monitoring
from dashboard.cluster_providers import (
    KubernetesAPIConfiguration,
    load_in_cluster_configuration,
    observe_argocd,
    observe_kubernetes,
)
from dashboard.lifecycle import (
    ArgoCDProviderData,
    KubernetesProviderData,
    aggregate_pipeline_run,
)
from dashboard.pipeline_context import (
    PIPELINE_FOLLOW_MODE,
    PIPELINE_INTERACTION_MODE_KEY,
    PIPELINE_LAST_OBSERVED_STAGE_KEY,
)

NOW = datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)
COMMIT_SHA = "9715faa3d0fc7c7a545ffaec5817adbac0592e91"


class _FakeAPI:
    def __init__(self, responses: dict[str, dict]) -> None:
        self.configuration = KubernetesAPIConfiguration(
            base_url="https://kubernetes.default.svc:443",
            token="not-exposed",
            certificate_authority=None,  # type: ignore[arg-type]
            dashboard_namespace="m-devops-dashboard",
            dashboard_deployment="m-devops-dashboard",
            argocd_namespace="argocd",
            argocd_application="m-devops-dashboard",
        )
        self.responses = responses

    def get(self, path: str) -> dict:
        return next(
            payload
            for suffix, payload in self.responses.items()
            if suffix in path
        )


def _workflow_snapshot(
    *,
    status: str = "completed",
    conclusion: str | None = "success",
) -> dict:
    return {
        "state": "Healthy",
        "repository": "hepi66/M_DevOps_Transformation",
        "branch": "main",
        "github_actions": {
            "availability": "available",
            "workflow": {
                "databaseId": 85,
                "number": 85,
                "name": "CI Pipeline",
                "status": status,
                "conclusion": conclusion,
                "headBranch": "main",
                "headSha": COMMIT_SHA,
                "createdAt": "2026-07-28T07:58:00Z",
                "startedAt": "2026-07-28T07:58:05Z",
                "updatedAt": "2026-07-28T08:00:00Z",
            },
            "jobs": [],
        },
        "ghcr": {
            "availability": "available",
            "tags": [COMMIT_SHA],
            "latest_tag": COMMIT_SHA,
            "digest": "sha256:abc",
            "published_at": "2026-07-28T08:00:00Z",
        },
        "refreshed_at": NOW.isoformat(),
    }


def test_in_cluster_configuration_selection_and_safe_local_fallback(tmp_path):
    assert load_in_cluster_configuration({}, service_account_directory=tmp_path) is None

    (tmp_path / "token").write_text("token-value", encoding="utf-8")
    (tmp_path / "ca.crt").write_text("certificate", encoding="utf-8")
    (tmp_path / "namespace").write_text(
        "m-devops-dashboard",
        encoding="utf-8",
    )
    configuration = load_in_cluster_configuration(
        {
            "KUBERNETES_SERVICE_HOST": "10.96.0.1",
            "KUBERNETES_SERVICE_PORT_HTTPS": "443",
        },
        service_account_directory=tmp_path,
    )

    assert configuration is not None
    assert configuration.base_url == "https://10.96.0.1:443"
    assert configuration.dashboard_namespace == "m-devops-dashboard"
    assert configuration.token == "token-value"


def test_argocd_provider_normalizes_live_application():
    api = _FakeAPI(
        {
            "m-devops-dashboard": {
                "metadata": {"name": "m-devops-dashboard"},
                "spec": {
                    "source": {"targetRevision": "main"},
                    "destination": {"namespace": "m-devops-dashboard"},
                },
                "status": {
                    "sync": {"status": "Synced", "revision": COMMIT_SHA},
                    "health": {"status": "Healthy"},
                    "operationState": {
                        "phase": "Succeeded",
                        "finishedAt": "2026-07-28T07:59:00Z",
                    },
                    "reconciledAt": "2026-07-28T08:00:00Z",
                },
            },
        }
    )

    observation = observe_argocd(api)

    assert observation.availability == "available"
    assert observation.operation_at is not None
    assert observation.status == "completed"
    assert observation.target_revision == "main"
    assert observation.observed_revision == COMMIT_SHA
    assert observation.namespace == "m-devops-dashboard"


def test_kubernetes_provider_normalizes_rollout_and_pods():
    api = _FakeAPI(
        {
            "/deployments/": {
                "metadata": {
                    "name": "m-devops-dashboard",
                    "annotations": {
                        "deployment.kubernetes.io/revision": "3",
                    },
                },
                "spec": {
                    "replicas": 1,
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "image": (
                                        "ghcr.io/hepi66/"
                                        f"m_devops_transformation:{COMMIT_SHA}"
                                    )
                                }
                            ]
                        }
                    },
                },
                "status": {
                    "availableReplicas": 1,
                    "updatedReplicas": 1,
                    "readyReplicas": 1,
                    "observedGeneration": 4,
                    "conditions": [],
                },
            },
            "/replicasets": {
                "items": [
                    {
                        "metadata": {
                            "annotations": {
                                "deployment.kubernetes.io/revision": "3"
                            }
                        }
                    }
                ]
            },
            "/pods": {
                "items": [
                    {
                        "metadata": {
                            "name": "dashboard-pod",
                            "creationTimestamp": "2026-07-28T07:59:00Z",
                        },
                        "spec": {
                            "containers": [
                                {
                                    "image": (
                                        "ghcr.io/hepi66/"
                                        f"m_devops_transformation:{COMMIT_SHA}"
                                    )
                                }
                            ]
                        },
                        "status": {
                            "phase": "Running",
                            "conditions": [
                                {"type": "Ready", "status": "True"}
                            ],
                            "containerStatuses": [
                                {
                                    "restartCount": 0,
                                    "imageID": (
                                        "docker-pullable://image@sha256:abc"
                                    ),
                                }
                            ],
                        },
                    }
                ]
            },
        }
    )

    observation = observe_kubernetes(api)

    assert observation.availability == "available"
    assert observation.status == "completed"
    assert observation.image_tag == COMMIT_SHA
    assert observation.image_digest == "sha256:abc"
    assert observation.image is not None
    assert observation.rollout_status == "Available"
    assert observation.replica_set_revision == "3"
    assert observation.pods[0].ready is True


def test_cluster_provider_failures_are_explicit_and_do_not_expose_token():
    class _UnavailableAPI(_FakeAPI):
        def get(self, path: str) -> dict:
            raise requests.ConnectionError("Bearer secret-token")

    api = _UnavailableAPI({})

    argocd = observe_argocd(api)
    kubernetes = observe_kubernetes(api)

    assert argocd.availability == "unavailable"
    assert kubernetes.availability == "unavailable"
    assert "secret-token" not in argocd.reason
    assert "secret-token" not in kubernetes.reason


def test_restart_reconstruction_uses_provider_evidence():
    argocd = ArgoCDProviderData(
        availability="available",
        status="completed",
        application="m-devops-dashboard",
        observed_revision=COMMIT_SHA,
        namespace="m-devops-dashboard",
        sync_status="Synced",
        health_status="Healthy",
    )
    kubernetes = KubernetesProviderData(
        availability="available",
        status="completed",
        namespace="m-devops-dashboard",
        deployment="m-devops-dashboard",
        image_tag=COMMIT_SHA,
        desired_replicas=1,
        available_replicas=1,
    )

    pipeline_run = aggregate_pipeline_run(
        _workflow_snapshot(),
        argocd_observation=argocd,
        kubernetes_observation=kubernetes,
    )

    assert pipeline_run.correlation_status == "correlated"
    assert pipeline_run.stage("argocd").status == "Completed"
    assert pipeline_run.stage("kubernetes").status == "Completed"
    assert pipeline_run.current_stage == "kubernetes"


def test_restart_reconstruction_can_use_immutable_runtime_image_without_github():
    kubernetes = KubernetesProviderData(
        availability="available",
        status="completed",
        namespace="m-devops-dashboard",
        deployment="m-devops-dashboard",
        image_tag=COMMIT_SHA,
        desired_replicas=1,
        available_replicas=1,
    )

    pipeline_run = aggregate_pipeline_run(
        {},
        kubernetes_observation=kubernetes,
    )

    assert pipeline_run.commit_sha == COMMIT_SHA
    assert pipeline_run.correlation_status == "partial"
    assert pipeline_run.stage("kubernetes").status == "Completed"
    assert pipeline_run.stage("ci").status == "Unknown"


def test_pipeline_stage_states_are_active_failed_and_neutral_from_evidence():
    active = aggregate_pipeline_run(
        _workflow_snapshot(status="in_progress", conclusion=None)
    )
    failed = aggregate_pipeline_run(
        _workflow_snapshot(status="completed", conclusion="failure")
    )
    neutral = aggregate_pipeline_run({})

    assert active.stage("code").status == "Completed"
    assert active.stage("ci").status == "Running"
    assert active.stage("argocd").status == "Unknown"
    assert failed.stage("ci").status == "Failed"
    assert failed.failed_stage == "ci"
    assert all(stage.status == "Unknown" for stage in neutral.stages)


def test_adaptive_refresh_intervals_and_next_refresh_calculation():
    active_run = aggregate_pipeline_run(
        _workflow_snapshot(status="in_progress", conclusion=None)
    )
    idle_run = aggregate_pipeline_run(_workflow_snapshot())
    unavailable_run = aggregate_pipeline_run({})

    assert monitoring.refresh_interval_for(active_run) == 7
    assert monitoring.refresh_interval_for(idle_run) == 20
    assert monitoring.refresh_interval_for(unavailable_run) == 20

    state = monitoring.refresh_monitoring_state(
        now=NOW,
        snapshot_loader=Mock(return_value=_workflow_snapshot()),
        cluster_loader=Mock(
            return_value=(
                ArgoCDProviderData(
                    availability="unavailable",
                    status="unavailable",
                ),
                KubernetesProviderData(
                    availability="unavailable",
                    status="unavailable",
                ),
            )
        ),
        clear_snapshot=Mock(),
    )
    assert state.next_refresh == NOW + timedelta(seconds=20)


def test_no_provider_retrieval_occurs_before_refresh_is_due(monkeypatch):
    pipeline_run = aggregate_pipeline_run(_workflow_snapshot())
    current = monitoring.MonitoringState(
        snapshot=_workflow_snapshot(),
        pipeline_run=pipeline_run,
        last_attempt=NOW,
        last_success=NOW,
        next_refresh=NOW + timedelta(seconds=20),
    )
    session_state = {
        monitoring.MONITORING_STATE_KEY: current,
        "operational_detail_source": "CI",
        PIPELINE_INTERACTION_MODE_KEY: PIPELINE_FOLLOW_MODE,
        PIPELINE_LAST_OBSERVED_STAGE_KEY: "CI",
    }
    refresh = Mock()
    monkeypatch.setattr(monitoring.st, "session_state", session_state)
    monkeypatch.setattr(monitoring, "refresh_monitoring_state", refresh)

    result = monitoring.ensure_monitoring_state(now=NOW)

    assert result is current
    refresh.assert_not_called()
    assert session_state["operational_detail_source"] == "CI"
    assert session_state[PIPELINE_INTERACTION_MODE_KEY] == PIPELINE_FOLLOW_MODE
    assert session_state[PIPELINE_LAST_OBSERVED_STAGE_KEY] == "CI"


def test_live_refresh_modes_control_fragment_scheduling():
    assert monitoring.automatic_refresh_interval(True) == 1
    assert monitoring.automatic_refresh_interval(False) is None


def test_live_refresh_off_preserves_due_monitoring_state(monkeypatch):
    pipeline_run = aggregate_pipeline_run(_workflow_snapshot())
    current = monitoring.MonitoringState(
        snapshot=_workflow_snapshot(),
        pipeline_run=pipeline_run,
        last_attempt=NOW,
        last_success=NOW,
        next_refresh=NOW,
    )
    session_state = {monitoring.MONITORING_STATE_KEY: current}
    refresh = Mock()
    monkeypatch.setattr(monitoring.st, "session_state", session_state)
    monkeypatch.setattr(monitoring, "refresh_monitoring_state", refresh)

    result = monitoring.ensure_monitoring_state(
        now=NOW + timedelta(seconds=60),
        automatic=False,
    )

    assert result is current
    refresh.assert_not_called()


def test_manual_refresh_performs_one_cycle_while_live_refresh_is_off(
    monkeypatch,
):
    pipeline_run = aggregate_pipeline_run(_workflow_snapshot())
    current = monitoring.MonitoringState(
        snapshot=_workflow_snapshot(),
        pipeline_run=pipeline_run,
        last_attempt=NOW,
        last_success=NOW,
        next_refresh=NOW + timedelta(seconds=20),
    )
    refreshed = monitoring.MonitoringState(
        snapshot=current.snapshot,
        pipeline_run=current.pipeline_run,
        last_attempt=NOW + timedelta(seconds=1),
        last_success=NOW + timedelta(seconds=1),
        next_refresh=NOW + timedelta(seconds=21),
    )
    session_state = {monitoring.MONITORING_STATE_KEY: current}
    refresh = Mock(return_value=refreshed)
    monkeypatch.setattr(monitoring.st, "session_state", session_state)
    monkeypatch.setattr(monitoring, "refresh_monitoring_state", refresh)

    monitoring.request_monitoring_refresh(now=NOW)
    result = monitoring.ensure_monitoring_state(
        now=NOW + timedelta(seconds=1),
        automatic=False,
    )

    assert result is refreshed
    refresh.assert_called_once()
    assert session_state[monitoring.FORCE_REFRESH_KEY] is False


def test_live_refresh_control_displays_explicit_off_mode(monkeypatch):
    sidebar = Mock()
    sidebar.toggle.return_value = False
    monkeypatch.setattr(monitoring.st, "sidebar", sidebar)
    monkeypatch.setattr(monitoring.st, "session_state", {})

    enabled = monitoring.render_live_refresh_control()

    assert enabled is False
    sidebar.caption.assert_called_once_with("OFF · Manual refresh only")


def test_manual_refresh_resets_schedule_without_changing_viewer_filter(monkeypatch):
    pipeline_run = aggregate_pipeline_run(_workflow_snapshot())
    current = monitoring.MonitoringState(
        snapshot=_workflow_snapshot(),
        pipeline_run=pipeline_run,
        last_attempt=NOW,
        last_success=NOW,
        next_refresh=NOW + timedelta(seconds=20),
    )
    session_state = {
        monitoring.MONITORING_STATE_KEY: current,
        "operational_detail_source": "Kubernetes",
    }
    monkeypatch.setattr(monitoring.st, "session_state", session_state)

    monitoring.request_monitoring_refresh(now=NOW)

    assert session_state[monitoring.FORCE_REFRESH_KEY] is True
    assert (
        session_state[monitoring.MONITORING_STATE_KEY].next_refresh
        == NOW
    )
    assert session_state["operational_detail_source"] == "Kubernetes"


def test_refresh_mechanics_do_not_create_operational_events():
    snapshot = _workflow_snapshot()
    pipeline_run = aggregate_pipeline_run(snapshot)
    state = monitoring.MonitoringState(
        snapshot=snapshot,
        pipeline_run=pipeline_run,
        last_attempt=NOW,
        last_success=NOW,
        next_refresh=NOW + timedelta(seconds=20),
    )

    assert "Refresh" not in monitoring.monitoring_status_text(state, now=NOW)
    assert "events" not in vars(state)


def _unavailable_cluster_observations():
    return (
        ArgoCDProviderData(
            availability="unavailable",
            status="unavailable",
        ),
        KubernetesProviderData(
            availability="unavailable",
            status="unavailable",
        ),
    )


def test_one_transient_ghcr_correlation_gap_preserves_completed_presentation():
    correlated_snapshot = _workflow_snapshot()
    previous = monitoring.refresh_monitoring_state(
        now=NOW,
        snapshot_loader=Mock(return_value=correlated_snapshot),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )
    interrupted_snapshot = _workflow_snapshot()
    interrupted_snapshot["ghcr"]["tags"] = ["latest"]
    interrupted_snapshot["ghcr"]["latest_tag"] = "latest"

    stabilized = monitoring.refresh_monitoring_state(
        previous,
        now=NOW + timedelta(seconds=7),
        snapshot_loader=Mock(return_value=interrupted_snapshot),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )

    assert stabilized.pipeline_run.stage("ghcr").status == "Completed"
    assert stabilized.ghcr_stability_cycles_remaining == 0


def test_repeated_uncorrelated_ghcr_snapshot_consumes_bounded_grace():
    correlated_snapshot = _workflow_snapshot()
    first = monitoring.refresh_monitoring_state(
        now=NOW,
        snapshot_loader=Mock(return_value=correlated_snapshot),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )
    uncorrelated_snapshot = _workflow_snapshot()
    uncorrelated_snapshot["ghcr"]["tags"] = ["latest"]
    uncorrelated_snapshot["ghcr"]["latest_tag"] = "latest"
    second = monitoring.refresh_monitoring_state(
        first,
        now=NOW + timedelta(seconds=7),
        snapshot_loader=Mock(return_value=uncorrelated_snapshot),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )

    third = monitoring.refresh_monitoring_state(
        second,
        now=NOW + timedelta(seconds=14),
        snapshot_loader=Mock(return_value=uncorrelated_snapshot),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )

    assert second.pipeline_run.stage("ghcr").status == "Completed"
    assert third.pipeline_run.stage("ghcr").status == "Unknown"


def test_transient_ghcr_unavailability_is_stabilized_once():
    first = monitoring.refresh_monitoring_state(
        now=NOW,
        snapshot_loader=Mock(return_value=_workflow_snapshot()),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )
    unavailable_snapshot = _workflow_snapshot()
    unavailable_snapshot["ghcr"] = {
        "availability": "unavailable",
        "reason": "Temporary registry response unavailable.",
    }

    second = monitoring.refresh_monitoring_state(
        first,
        now=NOW + timedelta(seconds=7),
        snapshot_loader=Mock(return_value=unavailable_snapshot),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )

    assert second.pipeline_run.stage("ghcr").status == "Completed"
    assert second.ghcr_stability_cycles_remaining == 0


def test_real_ghcr_failure_is_never_stabilized():
    first = monitoring.refresh_monitoring_state(
        now=NOW,
        snapshot_loader=Mock(return_value=_workflow_snapshot()),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )
    failed_snapshot = _workflow_snapshot()
    failed_snapshot["ghcr"] = {
        "availability": "available",
        "status": "failed",
        "tags": ["latest"],
    }

    failed = monitoring.refresh_monitoring_state(
        first,
        now=NOW + timedelta(seconds=7),
        snapshot_loader=Mock(return_value=failed_snapshot),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )

    assert failed.pipeline_run.stage("ghcr").status == "Failed"


def test_new_workflow_run_never_reuses_previous_ghcr_correlation():
    first = monitoring.refresh_monitoring_state(
        now=NOW,
        snapshot_loader=Mock(return_value=_workflow_snapshot()),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )
    new_run_snapshot = _workflow_snapshot()
    workflow = new_run_snapshot["github_actions"]["workflow"]
    workflow["databaseId"] = 86
    workflow["number"] = 86
    workflow["headSha"] = "b" * 40
    new_run_snapshot["ghcr"]["tags"] = ["latest"]

    new_run = monitoring.refresh_monitoring_state(
        first,
        now=NOW + timedelta(seconds=7),
        snapshot_loader=Mock(return_value=new_run_snapshot),
        cluster_loader=Mock(return_value=_unavailable_cluster_observations()),
        clear_snapshot=Mock(),
    )

    assert new_run.pipeline_run.stage("ghcr").status == "Unknown"
