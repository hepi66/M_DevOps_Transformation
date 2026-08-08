from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from dashboard.historical_telemetry import (
    HistoricalEvent,
    get_events_between,
)


@dataclass(frozen=True)
class DailyDoraBucket:
    """One UTC calendar-day projection of historical DORA evidence."""

    day: date
    deployment_count: int
    failed_deployment_count: int
    lead_time_average_seconds: float | None
    incident_count: int
    recovery_count: int


@dataclass(frozen=True)
class DoraMetrics:
    """Derived DORA-style evidence for one explicit observation window."""

    observation_start: datetime
    observation_end: datetime
    deployment_frequency: float
    successful_deployments: int
    failed_deployments: int
    lead_time_average_seconds: float | None
    change_failure_rate: float | None
    mttr_seconds: float | None
    incident_count: int
    recovery_count: int
    daily_buckets: tuple[DailyDoraBucket, ...]
    evidence_counts: dict[str, int]
    real_event_count: int
    synthetic_event_count: int


def seven_day_window(as_of: datetime) -> tuple[datetime, datetime]:
    """Return seven full UTC calendar days ending on the as-of UTC day."""
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("DORA observation timestamps must be timezone-aware.")
    utc_day = as_of.astimezone(timezone.utc).date()
    start = datetime.combine(
        utc_day - timedelta(days=6),
        time.min,
        tzinfo=timezone.utc,
    )
    end = datetime.combine(
        utc_day + timedelta(days=1),
        time.min,
        tzinfo=timezone.utc,
    )
    return start, end


def _average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _incident_recovery_durations(
    events: tuple[HistoricalEvent, ...],
) -> list[float]:
    starts: dict[str, datetime] = {}
    restorations: list[tuple[str, datetime]] = []
    for event in events:
        metadata = event.metadata or {}
        incident_id = metadata.get("incident_id")
        if not isinstance(incident_id, str) or not incident_id:
            continue
        if event.event_type == "incident_started":
            starts.setdefault(incident_id, event.occurred_at)
        elif event.event_type == "service_restored":
            restorations.append((incident_id, event.occurred_at))

    recovered: set[str] = set()
    durations: list[float] = []
    for incident_id, restored_at in sorted(
        restorations,
        key=lambda restoration: restoration[1],
    ):
        started_at = starts.get(incident_id)
        if (
            started_at is None
            or restored_at < started_at
            or incident_id in recovered
        ):
            continue
        durations.append((restored_at - started_at).total_seconds())
        recovered.add(incident_id)
    return durations


def aggregate_dora_metrics(
    *,
    as_of: datetime,
    database_path: Path | None = None,
    include_synthetic: bool = True,
) -> DoraMetrics:
    """Aggregate a seven-day derived view; lab events are included by default."""
    observation_start, observation_end = seven_day_window(as_of)
    stored_events = get_events_between(
        observation_start,
        observation_end,
        database_path,
    )
    events = tuple(
        event
        for event in stored_events
        if include_synthetic or not event.synthetic
    )
    successful = tuple(
        event
        for event in events
        if event.event_type == "deployment_succeeded"
    )
    failed = tuple(
        event
        for event in events
        if event.event_type == "deployment_failed"
    )
    lead_times = [
        float(event.duration_seconds)
        for event in successful
        if event.duration_seconds is not None
    ]
    deployment_total = len(successful) + len(failed)
    incidents = tuple(
        event for event in events if event.event_type == "incident_started"
    )
    recovery_durations = _incident_recovery_durations(events)
    evidence_counts = {
        event_type: sum(event.event_type == event_type for event in events)
        for event_type in sorted({event.event_type for event in events})
    }

    buckets: list[DailyDoraBucket] = []
    for offset in range(7):
        bucket_day = observation_start.date() + timedelta(days=offset)
        day_events = tuple(
            event
            for event in events
            if event.occurred_at.astimezone(timezone.utc).date() == bucket_day
        )
        day_successes = tuple(
            event
            for event in day_events
            if event.event_type == "deployment_succeeded"
        )
        day_lead_times = [
            float(event.duration_seconds)
            for event in day_successes
            if event.duration_seconds is not None
        ]
        buckets.append(
            DailyDoraBucket(
                day=bucket_day,
                deployment_count=len(day_successes),
                failed_deployment_count=sum(
                    event.event_type == "deployment_failed"
                    for event in day_events
                ),
                lead_time_average_seconds=_average(day_lead_times),
                incident_count=sum(
                    event.event_type == "incident_started"
                    for event in day_events
                ),
                recovery_count=sum(
                    event.event_type == "service_restored"
                    for event in day_events
                ),
            )
        )

    return DoraMetrics(
        observation_start=observation_start,
        observation_end=observation_end,
        deployment_frequency=len(successful) / 7,
        successful_deployments=len(successful),
        failed_deployments=len(failed),
        lead_time_average_seconds=_average(lead_times),
        change_failure_rate=(
            len(failed) / deployment_total if deployment_total else None
        ),
        mttr_seconds=_average(recovery_durations),
        incident_count=len(incidents),
        recovery_count=len(recovery_durations),
        daily_buckets=tuple(buckets),
        evidence_counts=evidence_counts,
        real_event_count=sum(not event.synthetic for event in events),
        synthetic_event_count=sum(event.synthetic for event in events),
    )
