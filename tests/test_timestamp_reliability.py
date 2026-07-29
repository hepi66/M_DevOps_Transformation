from datetime import datetime, timezone
from unittest.mock import Mock

from dashboard import operational_detail_viewer as viewer
from dashboard.formatting import (
    DASHBOARD_TIMESTAMP_FALLBACK,
    format_dashboard_timestamp,
    normalize_dashboard_timestamp,
)
from dashboard.operational_events import OperationalEvent


def _event(timestamp: object, event_id: str) -> OperationalEvent:
    return OperationalEvent(
        timestamp=timestamp,  # type: ignore[arg-type]
        source_identifier="GitHub Actions",
        source_abbreviation="CI",
        category="github",
        status="RUNNING",
        icon="▶",
        message="CI Pipeline running",
        event_id=event_id,
    )


def test_valid_timezone_aware_timestamp_preserves_dashboard_format():
    timestamp = datetime(2026, 7, 28, 8, 15, 30, tzinfo=timezone.utc)

    assert format_dashboard_timestamp(timestamp) == (
        timestamp.astimezone().strftime("%d %b %H:%M:%S")
    )


def test_valid_naive_timestamp_uses_consistent_local_time_behavior():
    timestamp = datetime(2026, 7, 28, 8, 15, 30)  # noqa: DTZ001

    assert format_dashboard_timestamp(timestamp) == (
        timestamp.astimezone().strftime("%d %b %H:%M:%S")
    )


def test_none_and_malformed_timestamps_use_neutral_fallback():
    assert format_dashboard_timestamp(None) == DASHBOARD_TIMESTAMP_FALLBACK
    assert (
        format_dashboard_timestamp("not-a-timestamp")
        == DASHBOARD_TIMESTAMP_FALLBACK
    )
    assert format_dashboard_timestamp(12345) == DASHBOARD_TIMESTAMP_FALLBACK


def test_windows_unsafe_and_extreme_datetimes_are_rejected():
    unsafe_values = (
        datetime.min.replace(tzinfo=timezone.utc),
        datetime.max.replace(tzinfo=timezone.utc),
        "0001-01-01T00:00:00Z",
        "9999-12-31T23:59:59Z",
    )

    for value in unsafe_values:
        assert normalize_dashboard_timestamp(value) is None
        assert format_dashboard_timestamp(value) == DASHBOARD_TIMESTAMP_FALLBACK


def test_epoch_zero_remains_a_valid_real_timestamp():
    assert (
        format_dashboard_timestamp("1970-01-01T00:00:00Z")
        != DASHBOARD_TIMESTAMP_FALLBACK
    )


def test_one_invalid_event_timestamp_cannot_break_complete_timeline(
    monkeypatch,
):
    rendered = Mock()
    monkeypatch.setattr(viewer.st, "html", rendered)
    events = [
        _event("2026-07-28T08:15:30Z", "valid"),
        _event(datetime.min.replace(tzinfo=timezone.utc), "invalid"),
    ]

    viewer._render_event_timeline(events)

    rendered_html = rendered.call_args.args[0]
    assert "28 Jul" in rendered_html
    assert DASHBOARD_TIMESTAMP_FALLBACK in rendered_html
    assert rendered_html.count('<div class="event-row') == 2


def test_active_github_workflow_sentinel_completion_times_are_removed(
    monkeypatch,
):
    run = {
        "databaseId": 99,
        "name": "CI Pipeline",
        "status": "in_progress",
        "conclusion": None,
        "createdAt": "2026-07-28T08:00:00Z",
        "startedAt": "2026-07-28T08:00:05Z",
        "updatedAt": "2026-07-28T08:01:00Z",
    }
    jobs = {
        "jobs": [
            {
                "name": "build",
                "status": "in_progress",
                "conclusion": None,
                "startedAt": "2026-07-28T08:01:05Z",
                "completedAt": "0001-01-01T00:00:00Z",
                "steps": [
                    {
                        "name": "Build and push",
                        "status": "in_progress",
                        "conclusion": None,
                        "startedAt": "2026-07-28T08:01:10Z",
                        "completedAt": "0001-01-01T00:00:00Z",
                    }
                ],
            }
        ]
    }
    monkeypatch.setattr(viewer, "_run_gh_json", Mock(return_value=jobs))

    actions = viewer._load_github_actions_details(
        [run],
        workflow_name="CI Pipeline",
    )
    docker_build = viewer._project_docker_build(
        actions,
        job_name="build",
        step_name="Build and push",
    )
    snapshot = {
        "github_actions": actions,
        "docker_build": docker_build,
    }
    events = viewer._build_docker_build_feed(snapshot)

    assert actions["jobs"][0]["completedAt"] is None
    assert actions["jobs"][0]["steps"][0]["completedAt"] is None
    assert events
    assert all(
        event.timestamp is None
        or not event.timestamp.startswith("0001-")
        for event in events
    )
    assert all("completed successfully" not in event.message for event in events)


def test_event_construction_rejects_sentinel_before_rendering():
    event = viewer._operational_event(
        timestamp="0001-01-01T00:00:00Z",
        source="CI",
        category="github",
        status="RUNNING",
        message="Workflow running",
        order=1,
        event_id="workflow:running",
    )

    assert event.timestamp is None
