from datetime import date, datetime, timedelta, timezone

import pytest

from dashboard.dora_metrics import aggregate_dora_metrics, seven_day_window
from dashboard.historical_telemetry import HistoricalEvent, insert_event
from scripts.seed_dashboard_history import lab_history_events, seed_lab_history

AS_OF = datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc)
START, END = seven_day_window(AS_OF)
RELEASE_SHA = "a" * 40


def _store(
    database,
    event_id,
    event_type,
    occurred_at,
    *,
    duration_seconds=None,
    synthetic=False,
    metadata=None,
):
    insert_event(
        HistoricalEvent(
            event_id=event_id,
            event_type=event_type,
            occurred_at=occurred_at,
            release_sha=RELEASE_SHA,
            environment="m-devops-dashboard",
            source="monitoring",
            status=None,
            duration_seconds=duration_seconds,
            synthetic=synthetic,
            metadata=metadata,
        ),
        database,
    )


def test_seven_daily_buckets_and_deployment_frequency(tmp_path):
    database = tmp_path / "history.db"
    _store(database, "one", "deployment_succeeded", START)
    _store(
        database,
        "two",
        "deployment_succeeded",
        START + timedelta(days=2),
    )
    _store(
        database,
        "three",
        "deployment_succeeded",
        START + timedelta(days=6, hours=23),
    )

    metrics = aggregate_dora_metrics(as_of=AS_OF, database_path=database)

    assert len(metrics.daily_buckets) == 7
    assert [bucket.day for bucket in metrics.daily_buckets] == [
        START.date() + timedelta(days=offset) for offset in range(7)
    ]
    assert [bucket.deployment_count for bucket in metrics.daily_buckets] == [
        1,
        0,
        1,
        0,
        0,
        0,
        1,
    ]
    assert metrics.successful_deployments == 3
    assert metrics.deployment_frequency == pytest.approx(3 / 7)


def test_zero_deployments_returns_unavailable_rates(tmp_path):
    metrics = aggregate_dora_metrics(
        as_of=AS_OF,
        database_path=tmp_path / "empty.db",
    )

    assert metrics.successful_deployments == 0
    assert metrics.deployment_frequency == 0
    assert metrics.change_failure_rate is None
    assert metrics.lead_time_average_seconds is None


def test_lead_time_averages_only_explicit_success_durations(tmp_path):
    database = tmp_path / "history.db"
    _store(
        database,
        "qualified-one",
        "deployment_succeeded",
        START,
        duration_seconds=600,
    )
    _store(
        database,
        "missing",
        "deployment_succeeded",
        START + timedelta(days=1),
    )
    _store(
        database,
        "qualified-two",
        "deployment_succeeded",
        START + timedelta(days=2),
        duration_seconds=900,
    )
    _store(
        database,
        "failed-duration",
        "deployment_failed",
        START + timedelta(days=3),
        duration_seconds=1,
    )

    metrics = aggregate_dora_metrics(as_of=AS_OF, database_path=database)

    assert metrics.lead_time_average_seconds == 750
    assert metrics.daily_buckets[1].lead_time_average_seconds is None


def test_change_failure_rate_uses_only_deployment_outcomes(tmp_path):
    database = tmp_path / "history.db"
    for index in range(3):
        _store(
            database,
            f"success-{index}",
            "deployment_succeeded",
            START + timedelta(days=index),
        )
    _store(
        database,
        "failure",
        "deployment_failed",
        START + timedelta(days=3),
    )
    _store(
        database,
        "incident",
        "incident_started",
        START + timedelta(days=3, minutes=5),
        metadata={"incident_id": "incident-1"},
    )

    metrics = aggregate_dora_metrics(as_of=AS_OF, database_path=database)

    assert metrics.failed_deployments == 1
    assert metrics.change_failure_rate == 0.25


def test_mttr_uses_only_correlated_incident_recovery_pairs(tmp_path):
    database = tmp_path / "history.db"
    _store(
        database,
        "incident-one",
        "incident_started",
        START + timedelta(days=2, hours=1),
        metadata={"incident_id": "incident-1"},
    )
    _store(
        database,
        "restore-one",
        "service_restored",
        START + timedelta(days=2, hours=1, minutes=20),
        metadata={"incident_id": "incident-1"},
    )
    _store(
        database,
        "incident-open",
        "incident_started",
        START + timedelta(days=3),
        metadata={"incident_id": "incident-open"},
    )
    _store(
        database,
        "restore-unmatched",
        "service_restored",
        START + timedelta(days=4),
        metadata={"incident_id": "unknown"},
    )

    metrics = aggregate_dora_metrics(as_of=AS_OF, database_path=database)

    assert metrics.incident_count == 2
    assert metrics.recovery_count == 1
    assert metrics.mttr_seconds == 20 * 60


def test_incomplete_incident_has_unavailable_mttr(tmp_path):
    database = tmp_path / "history.db"
    _store(
        database,
        "incident-open",
        "incident_started",
        START,
        metadata={"incident_id": "open"},
    )

    metrics = aggregate_dora_metrics(as_of=AS_OF, database_path=database)

    assert metrics.incident_count == 1
    assert metrics.recovery_count == 0
    assert metrics.mttr_seconds is None


def test_real_and_synthetic_counts_can_exclude_lab_events(tmp_path):
    database = tmp_path / "history.db"
    _store(database, "real", "deployment_succeeded", START)
    _store(
        database,
        "lab",
        "deployment_succeeded",
        START + timedelta(days=1),
        synthetic=True,
    )

    combined = aggregate_dora_metrics(as_of=AS_OF, database_path=database)
    observed = aggregate_dora_metrics(
        as_of=AS_OF,
        database_path=database,
        include_synthetic=False,
    )

    assert combined.real_event_count == 1
    assert combined.synthetic_event_count == 1
    assert combined.successful_deployments == 2
    assert observed.real_event_count == 1
    assert observed.synthetic_event_count == 0
    assert observed.successful_deployments == 1


def test_seed_is_deterministic_idempotent_and_preserves_real_events(tmp_path):
    database = tmp_path / "history.db"
    _store(database, "real-event", "deployment_succeeded", START)

    first = seed_lab_history(database, AS_OF.date())
    second = seed_lab_history(database, AS_OF.date())
    metrics = aggregate_dora_metrics(as_of=AS_OF, database_path=database)

    assert first == (6, 0)
    assert second == (0, 6)
    assert metrics.real_event_count == 1
    assert metrics.synthetic_event_count == 6
    assert "real-event" not in {
        event.event_id for event in lab_history_events(AS_OF.date())
    }
    assert lab_history_events(AS_OF.date()) == lab_history_events(AS_OF.date())


def test_utc_window_includes_start_and_excludes_end(tmp_path):
    database = tmp_path / "history.db"
    _store(database, "start", "deployment_succeeded", START)
    _store(
        database,
        "before-start",
        "deployment_succeeded",
        START - timedelta(microseconds=1),
    )
    _store(
        database,
        "before-end",
        "deployment_succeeded",
        END - timedelta(microseconds=1),
    )
    _store(database, "end", "deployment_succeeded", END)

    metrics = aggregate_dora_metrics(as_of=AS_OF, database_path=database)

    assert metrics.successful_deployments == 2
    assert metrics.daily_buckets[0].deployment_count == 1
    assert metrics.daily_buckets[-1].deployment_count == 1


def test_seed_pattern_is_small_coherent_and_fully_synthetic():
    events = lab_history_events(date(2026, 8, 8))

    assert len(events) == 6
    assert all(event.synthetic for event in events)
    assert sum(event.event_type == "deployment_succeeded" for event in events) == 3
    assert sum(event.event_type == "deployment_failed" for event in events) == 1
    assert sum(event.event_type == "incident_started" for event in events) == 1
    assert sum(event.event_type == "service_restored" for event in events) == 1
