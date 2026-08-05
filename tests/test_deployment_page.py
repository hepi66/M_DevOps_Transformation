from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock

from dashboard import deployment_page, navigation
from dashboard.lifecycle import aggregate_pipeline_run
from dashboard.monitoring import MonitoringState

NOW = datetime(2026, 8, 4, 8, 0, tzinfo=timezone.utc)
COMMIT_SHA = "9715faa3d0fc7c7a545ffaec5817adbac0592e91"
IMAGE = f"ghcr.io/hepi66/m_devops_transformation:{COMMIT_SHA}"
DIGEST = "sha256:abc123"


def _snapshot(*, sync_status: str = "Synced") -> dict:
    return {
        "repository": "hepi66/M_DevOps_Transformation",
        "branch": "main",
        "github_actions": {
            "availability": "available",
            "workflow": {
                "databaseId": 95,
                "number": 95,
                "name": "CI Pipeline",
                "status": "completed",
                "conclusion": "success",
                "headSha": COMMIT_SHA,
                "headBranch": "main",
                "createdAt": "2026-08-04T07:50:00Z",
                "startedAt": "2026-08-04T07:51:00Z",
                "updatedAt": "2026-08-04T07:55:00Z",
            },
            "jobs": [],
        },
        "ghcr": {
            "availability": "available",
            "tags": ["latest", COMMIT_SHA],
            "latest_tag": "latest",
            "image_name": "ghcr.io/hepi66/m_devops_transformation",
            "digest": DIGEST,
            "published_at": "2026-08-04T07:56:00Z",
        },
        "argocd": {
            "availability": "available",
            "application": "m-devops-dashboard",
            "target_revision": "main",
            "observed_revision": COMMIT_SHA,
            "namespace": "m-devops-dashboard",
            "sync_status": sync_status,
            "health_status": "Healthy",
            "operation_phase": "Succeeded",
            "operation_at": "2026-08-04T07:58:00Z",
        },
        "kubernetes": {
            "availability": "available",
            "namespace": "m-devops-dashboard",
            "deployment": "m-devops-dashboard",
            "deployment_revision": "4",
            "image": IMAGE,
            "image_tag": COMMIT_SHA,
            "image_digest": DIGEST,
            "desired_replicas": 1,
            "updated_replicas": 1,
            "ready_replicas": 1,
            "available_replicas": 1,
            "rollout_status": "Available",
            "replica_set_revision": "4",
            "pods": [
                {
                    "name": "m-devops-dashboard-abc",
                    "phase": "Running",
                    "ready": True,
                    "restart_count": 0,
                    "image": IMAGE,
                    "image_digest": DIGEST,
                    "created_at": "2026-08-04T07:58:30Z",
                }
            ],
        },
        "refreshed_at": NOW.isoformat(),
    }


def _monitoring_state(snapshot: dict) -> MonitoringState:
    pipeline_run = aggregate_pipeline_run(snapshot)
    return MonitoringState(
        snapshot=snapshot,
        pipeline_run=pipeline_run,
        last_attempt=NOW,
        last_success=NOW,
        next_refresh=NOW + timedelta(seconds=45),
    )


def test_navigation_contains_deployments_and_preserves_overview(monkeypatch):
    class SessionState(dict):
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__

    captured_pages = {}
    sidebar = Mock()

    def choose_deployments(_label, pages, **_kwargs):
        captured_pages.update(pages)
        return "🚀 Deployments"

    sidebar.radio.side_effect = choose_deployments
    fake_streamlit = Mock(sidebar=sidebar, session_state=SessionState())
    monkeypatch.setattr(navigation, "st", fake_streamlit)

    selected_page = navigation.render_navigation(show_refresh_control=False)

    assert selected_page == "deployments"
    assert captured_pages == {
        "🏠 Overview": "overview",
        "🚀 Deployments": "deployments",
    }


def test_healthy_synced_deployment_is_fully_correlated():
    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(_snapshot())
    )

    assert page_state.overall_status == "Healthy"
    assert page_state.replicas == "1 / 1 Ready"
    assert page_state.correlation_status == "Correlated"
    assert page_state.desired_image == IMAGE
    assert page_state.running_image == IMAGE
    assert page_state.running_digest == DIGEST


def test_healthy_outofsync_remains_healthy_and_visible_separately():
    pipeline_run = aggregate_pipeline_run(_snapshot(sync_status="OutOfSync"))
    page_state = deployment_page.build_deployment_page_state(pipeline_run)

    assert page_state.overall_status == "Healthy"
    assert pipeline_run.argocd.sync_status == "OutOfSync"
    assert pipeline_run.argocd.health_status == "Healthy"


def test_unavailable_and_missing_runtime_identity_are_safe():
    snapshot = _snapshot()
    snapshot["argocd"] = {
        "availability": "unavailable",
        "reason": "Provider unavailable",
    }
    snapshot["kubernetes"] = {
        "availability": "unavailable",
        "reason": "Provider unavailable",
    }
    snapshot["ghcr"].pop("digest")
    pipeline_run = aggregate_pipeline_run(snapshot)

    page_state = deployment_page.build_deployment_page_state(pipeline_run)

    assert page_state.overall_status == "Unavailable"
    assert page_state.replicas == "Unavailable"
    assert page_state.desired_image is None
    assert page_state.running_image is None
    assert page_state.running_digest is None


def test_pod_and_runtime_information_remain_normalized():
    pipeline_run = aggregate_pipeline_run(_snapshot())
    kubernetes = pipeline_run.kubernetes

    assert kubernetes.deployment_revision == "4"
    assert kubernetes.replica_set_revision == "4"
    assert kubernetes.ready_replicas == 1
    assert kubernetes.pods[0].name == "m-devops-dashboard-abc"
    assert kubernetes.pods[0].phase == "Running"
    assert kubernetes.pods[0].ready is True
    assert kubernetes.pods[0].restart_count == 0


def test_deployment_page_renders_all_sections(monkeypatch):
    section_names = (
        "_render_current_deployment",
        "_render_release_identity",
        "_render_gitops_status",
        "_render_kubernetes_runtime",
        "_render_access",
        "_render_deployment_journey",
    )
    sections = {name: Mock() for name in section_names}
    for name, renderer in sections.items():
        monkeypatch.setattr(deployment_page, name, renderer)
    columns = [MagicMock(), MagicMock()]
    monkeypatch.setattr(deployment_page.st, "columns", Mock(return_value=columns))
    caption = Mock()
    monkeypatch.setattr(deployment_page.st, "caption", caption)

    state = _monitoring_state(_snapshot())
    deployment_page.render_deployment_page(state)

    assert all(renderer.called for renderer in sections.values())
    caption.assert_called_once_with("Monitoring snapshot: 04 Aug 10:00:00")


def test_access_section_is_explicit_and_does_not_start_port_forward(monkeypatch):
    fake_streamlit = MagicMock()
    fake_streamlit.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr(deployment_page, "st", fake_streamlit)
    monkeypatch.setattr(deployment_page, "render_component_header", Mock())

    deployment_page._render_access()

    fake_streamlit.code.assert_called_once_with(
        deployment_page.PORT_FORWARD_COMMAND,
        language="powershell",
    )
    fake_streamlit.link_button.assert_called_once_with(
        "Open Dashboard",
        "http://127.0.0.1:8501",
    )
    explanation = fake_streamlit.info.call_args.args[0]
    assert "already-running ClusterIP Service" in explanation
    assert "does not start or deploy" in explanation
    assert not hasattr(deployment_page, "subprocess")
