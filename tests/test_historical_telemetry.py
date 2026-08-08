import sqlite3
from datetime import datetime, timedelta, timezone

from dashboard import historical_telemetry as telemetry
from dashboard import monitoring
from dashboard.lifecycle import (
    ArgoCDProviderData,
    KubernetesProviderData,
    aggregate_pipeline_run,
)

NOW = datetime(2026, 8, 8, 8, 0, tzinfo=timezone.utc)
COMMIT_SHA = "c13ebf132296a6782e9bab62df7fa62a5f51774f"


def _event(
    event_id: str,
    occurred_at: datetime,
    *,
    synthetic: bool = False,
) -> telemetry.HistoricalEvent:
    return telemetry.HistoricalEvent(
        event_id=event_id,
        event_type="deployment_succeeded",
        occurred_at=occurred_at,
        release_sha=COMMIT_SHA,
        environment="m-devops-dashboard",
        source="argocd",
        status="succeeded",
        synthetic=synthetic,
        metadata={"application": "m-devops-dashboard"},
    )


def _providers(
    *,
    phase: str = "Succeeded",
    argocd_status: str = "completed",
    kubernetes_status: str = "completed",
) -> tuple[ArgoCDProviderData, KubernetesProviderData]:
    return (
        ArgoCDProviderData(
            availability="available",
            status=argocd_status,  # type: ignore[arg-type]
            application="m-devops-dashboard",
            namespace="m-devops-dashboard",
            sync_status="Synced",
            health_status="Healthy",
            operation_phase=phase,
            operation_at=NOW,
        ),
        KubernetesProviderData(
            availability="available",
            status=kubernetes_status,  # type: ignore[arg-type]
            namespace="m-devops-dashboard",
            deployment="m-devops-dashboard",
            image=(
                "ghcr.io/hepi66/m_devops_transformation:"
                f"{COMMIT_SHA}"
            ),
            image_tag=COMMIT_SHA,
            image_digest="sha256:abc123",
            desired_replicas=1,
            ready_replicas=1,
            available_replicas=1,
        ),
    )


def _pipeline_run(
    *,
    phase: str = "Succeeded",
    argocd_status: str = "completed",
    kubernetes_status: str = "completed",
):
    argocd, kubernetes = _providers(
        phase=phase,
        argocd_status=argocd_status,
        kubernetes_status=kubernetes_status,
    )
    return aggregate_pipeline_run(
        {},
        argocd_observation=argocd,
        kubernetes_observation=kubernetes,
    )


def test_schema_initializes_on_empty_database(tmp_path):
    database = tmp_path / "history.db"

    telemetry.initialize_schema(database)

    with sqlite3.connect(database) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert {"schema_version", "historical_events"} <= tables


def test_insert_is_idempotent_and_retains_different_events(tmp_path):
    database = tmp_path / "history.db"
    first = _event("event-1", NOW)
    second = _event("event-2", NOW + timedelta(minutes=1))

    assert telemetry.insert_event(first, database) is True
    assert telemetry.insert_event(first, database) is False
    assert telemetry.insert_event(second, database) is True
    assert telemetry.count_events(database) == 2


def test_time_range_preserves_sha_utc_synthetic_and_metadata(tmp_path):
    database = tmp_path / "history.db"
    local_time = datetime(
        2026,
        8,
        8,
        10,
        0,
        tzinfo=timezone(timedelta(hours=2)),
    )
    telemetry.insert_event(_event("real", local_time), database)
    telemetry.insert_event(
        _event("synthetic", local_time + timedelta(days=1), synthetic=True),
        database,
    )

    events = telemetry.get_events_between(
        NOW - timedelta(days=6),
        NOW + timedelta(days=2),
        database,
    )

    assert [event.event_id for event in events] == ["real", "synthetic"]
    assert events[0].occurred_at == NOW
    assert events[0].release_sha == COMMIT_SHA
    assert events[0].synthetic is False
    assert events[1].synthetic is True
    assert events[0].metadata == {"application": "m-devops-dashboard"}


def test_recent_and_since_queries_hide_sql_from_consumers(tmp_path):
    database = tmp_path / "history.db"
    for index in range(3):
        telemetry.insert_event(
            _event(f"event-{index}", NOW + timedelta(days=index)),
            database,
        )

    since = telemetry.get_events_since(NOW + timedelta(days=1), database)
    recent = telemetry.get_recent_events(2, database)

    assert [event.event_id for event in since] == ["event-1", "event-2"]
    assert [event.event_id for event in recent] == ["event-2", "event-1"]


def test_successful_deployment_uses_normalized_provider_evidence():
    events = telemetry.events_from_pipeline_run(_pipeline_run())

    assert len(events) == 1
    assert events[0].event_type == "deployment_succeeded"
    assert events[0].occurred_at == NOW
    assert events[0].release_sha == COMMIT_SHA
    assert events[0].environment == "m-devops-dashboard"
    assert events[0].source == "argocd"
    assert events[0].duration_seconds is None
    assert events[0].synthetic is False


def test_explicit_failed_argocd_operation_is_recorded():
    events = telemetry.events_from_pipeline_run(
        _pipeline_run(phase="Failed", argocd_status="failed")
    )

    assert len(events) == 1
    assert events[0].event_type == "deployment_failed"
    assert events[0].status == "failed"


def test_unsupported_or_incomplete_evidence_is_not_recorded():
    run = _pipeline_run()
    incomplete_argocd = ArgoCDProviderData(
        availability="available",
        status="completed",
        operation_phase="Succeeded",
        operation_at=None,
    )
    incomplete = aggregate_pipeline_run(
        {},
        argocd_observation=incomplete_argocd,
        kubernetes_observation=run.kubernetes,
    )

    assert telemetry.events_from_pipeline_run(incomplete) == ()


def test_invalid_database_path_fails_gracefully_at_integration_boundary(
    tmp_path,
    monkeypatch,
):
    parent_file = tmp_path / "not-a-directory"
    parent_file.write_text("blocked", encoding="utf-8")
    monkeypatch.setenv(
        telemetry.HISTORY_DB_ENVIRONMENT_VARIABLE,
        str(parent_file / "history.db"),
    )

    assert telemetry.record_pipeline_events_safely(_pipeline_run()) is False


def test_monitoring_refresh_deduplicates_repeated_deployment_observation(
    tmp_path,
    monkeypatch,
):
    database = tmp_path / "history.db"
    monkeypatch.setenv(
        telemetry.HISTORY_DB_ENVIRONMENT_VARIABLE,
        str(database),
    )
    argocd, kubernetes = _providers()
    cluster_loader = lambda: (argocd, kubernetes)

    first = monitoring.refresh_monitoring_state(
        now=NOW,
        snapshot_loader=dict,
        cluster_loader=cluster_loader,
        clear_snapshot=lambda: None,
    )
    second = monitoring.refresh_monitoring_state(
        previous=first,
        now=NOW + timedelta(seconds=45),
        snapshot_loader=dict,
        cluster_loader=cluster_loader,
        clear_snapshot=lambda: None,
    )

    assert telemetry.count_events(database) == 1
    assert first.pipeline_run.commit_sha == second.pipeline_run.commit_sha
    assert first.pipeline_run.stages == second.pipeline_run.stages
    assert first.pipeline_run.kubernetes == second.pipeline_run.kubernetes


def test_recording_does_not_mutate_pipeline_run(tmp_path):
    pipeline_run = _pipeline_run()

    telemetry.record_pipeline_events(pipeline_run, tmp_path / "history.db")

    assert pipeline_run == _pipeline_run()
