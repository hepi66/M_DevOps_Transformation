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


def test_deployed_release_is_extracted_from_full_desired_image_sha():
    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(_snapshot())
    )

    assert page_state.release_sha == COMMIT_SHA
    assert deployment_page._short_release(page_state.release_sha) == COMMIT_SHA[:7]
    assert page_state.desired_evidence == "Confirmed"


def test_matching_desired_and_running_images_confirm_runtime_artifact():
    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(_snapshot())
    )

    assert page_state.desired_image == page_state.running_image
    assert page_state.running_evidence == "Confirmed"


def test_running_image_mismatch_is_reported_as_conflict():
    snapshot = _snapshot()
    other_sha = "a" * 40
    snapshot["kubernetes"]["pods"][0]["image"] = (
        f"ghcr.io/hepi66/m_devops_transformation:{other_sha}"
    )

    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    assert page_state.running_evidence == "Conflict"
    assert page_state.correlation_status == "Conflict detected"


def test_newer_repository_head_does_not_replace_deployed_release():
    snapshot = _snapshot()
    snapshot["github_actions"]["workflow"]["headSha"] = "b" * 40

    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    assert page_state.release_sha == COMMIT_SHA
    assert page_state.workflow_identity is None
    assert page_state.correlation_status == "Correlated"


def test_newer_latest_artifact_does_not_false_confirm_deployed_release():
    snapshot = _snapshot()
    snapshot["github_actions"]["workflow"]["headSha"] = "b" * 40
    snapshot["ghcr"]["tags"] = ["latest", "b" * 40]

    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    assert page_state.release_sha == COMMIT_SHA
    assert page_state.ghcr_evidence == "Unavailable"
    assert page_state.published_tag is None
    assert page_state.correlation_status == "Partially correlated"


def test_exact_deployed_ghcr_tag_confirms_release_artifact():
    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(_snapshot())
    )

    assert page_state.ghcr_evidence == "Confirmed"
    assert page_state.published_tag == COMMIT_SHA


def test_missing_deployed_ghcr_tag_remains_unavailable():
    snapshot = _snapshot()
    snapshot["ghcr"]["tags"] = ["latest"]

    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    assert page_state.ghcr_evidence == "Unavailable"
    assert page_state.correlation_status == "Partially correlated"


def test_complete_correlation_has_no_explanatory_warning():
    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(_snapshot())
    )

    assert deployment_page.release_correlation_explanation(page_state) is None


def test_partial_correlation_explains_confirmed_and_unavailable_evidence():
    snapshot = _snapshot()
    snapshot["ghcr"]["tags"] = ["latest"]
    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    explanation = deployment_page.release_correlation_explanation(page_state)

    assert explanation == (
        "unavailable",
        "3 of 4 release signals confirmed · Unavailable: GHCR artifact",
    )


def test_conflict_explanation_is_distinct_from_unavailable_evidence():
    snapshot = _snapshot()
    snapshot["ghcr"]["tags"] = ["latest"]
    snapshot["kubernetes"]["pods"][0]["image"] = (
        f"ghcr.io/hepi66/m_devops_transformation:{'a' * 40}"
    )
    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    explanation = deployment_page.release_correlation_explanation(page_state)

    assert explanation == (
        "conflict",
        "2 of 4 release signals confirmed · Conflict: Running artifact",
    )
    assert "Unavailable" not in explanation[1]


def test_short_or_unrelated_ghcr_tag_does_not_confirm_release():
    snapshot = _snapshot()
    snapshot["ghcr"]["tags"] = [COMMIT_SHA[:7], "c" * 40]

    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    assert page_state.ghcr_evidence == "Unavailable"


def test_missing_digest_does_not_hide_exact_tag_evidence():
    snapshot = _snapshot()
    snapshot["ghcr"].pop("digest")
    snapshot["kubernetes"].pop("image_digest")
    snapshot["kubernetes"]["pods"][0].pop("image_digest")

    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    assert page_state.ghcr_evidence == "Confirmed"
    assert page_state.running_digest is None
    assert page_state.correlation_status == "Correlated"


def test_non_immutable_desired_image_is_not_treated_as_release_identity():
    snapshot = _snapshot()
    snapshot["kubernetes"]["image"] = (
        "ghcr.io/hepi66/m_devops_transformation:latest"
    )
    snapshot["kubernetes"]["image_tag"] = "latest"

    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    assert page_state.release_sha == COMMIT_SHA
    assert page_state.desired_evidence == "Unavailable"
    assert page_state.running_evidence == "Confirmed"
    assert page_state.correlation_status == "Partially correlated"


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


def test_partial_release_correlation_remains_visible():
    snapshot = _snapshot()
    snapshot["argocd"] = {
        "availability": "unavailable",
        "reason": "Provider unavailable",
    }
    snapshot["kubernetes"] = {
        "availability": "unavailable",
        "reason": "Provider unavailable",
    }

    page_state = deployment_page.build_deployment_page_state(
        aggregate_pipeline_run(snapshot)
    )

    assert page_state.correlation_status == "Partially correlated"


def test_partial_monitoring_status_names_available_providers():
    snapshot = _snapshot()
    snapshot["argocd"] = {
        "availability": "unavailable",
        "reason": "Provider unavailable",
    }
    state = _monitoring_state(snapshot)

    status = deployment_page.deployment_monitoring_status_text(state)

    assert status.startswith("Partial live data")
    assert "GitHub" in status
    assert "GHCR" in status
    assert "Kubernetes" in status
    assert "Argo CD" not in status


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
        "_render_deployment_summary",
        "_render_current_release",
        "_render_gitops_status",
        "_render_kubernetes_runtime",
        "_render_technical_details",
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
    timestamp_formatter = Mock(return_value="formatted snapshot time")
    monkeypatch.setattr(
        deployment_page,
        "format_dashboard_timestamp",
        timestamp_formatter,
    )

    state = _monitoring_state(_snapshot())
    deployment_page.render_deployment_page(state)

    assert all(renderer.called for renderer in sections.values())
    timestamp_formatter.assert_called_once_with(NOW)
    caption.assert_called_once_with("Monitoring snapshot: formatted snapshot time")


def test_technical_details_remain_available_in_expander(monkeypatch):
    fake_streamlit = MagicMock()
    fake_streamlit.columns.return_value = [MagicMock(), MagicMock()]
    monkeypatch.setattr(deployment_page, "st", fake_streamlit)

    pipeline_run = aggregate_pipeline_run(_snapshot())
    page_state = deployment_page.build_deployment_page_state(pipeline_run)
    deployment_page._render_technical_details(pipeline_run, page_state)

    fake_streamlit.expander.assert_called_once_with("Technical Details")
    rendered_code_values = {
        call.args[0] for call in fake_streamlit.code.call_args_list
    }
    assert COMMIT_SHA in rendered_code_values
    assert IMAGE in rendered_code_values
    assert DIGEST in rendered_code_values


def test_access_section_is_explicit_and_does_not_start_port_forward(monkeypatch):
    fake_streamlit = MagicMock()
    fake_streamlit.columns.return_value = [
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    ]
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
    assert "only while a suitable port-forward is active" in explanation
    assert not hasattr(deployment_page, "subprocess")


def test_deployment_journey_remains_available_in_expander(monkeypatch):
    fake_streamlit = MagicMock()
    monkeypatch.setattr(deployment_page, "st", fake_streamlit)

    deployment_page._render_deployment_journey()

    fake_streamlit.expander.assert_called_once_with("Deployment Journey")
    journey = fake_streamlit.markdown.call_args.args[0]
    assert "GitHub Actions" in journey
    assert "Immutable SHA Promotion" in journey
    assert "Kubernetes Deployment" in journey
