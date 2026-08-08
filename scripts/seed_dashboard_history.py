from __future__ import annotations

import argparse
import hashlib
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from dashboard.historical_telemetry import (
    HistoricalEvent,
    history_database_path,
    insert_event,
)

LAB_DATASET = "linkedin-7-day-lab"


def _identifier(*parts: object) -> str:
    value = "|".join(str(part) for part in parts)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _release_sha(day: date, sequence: int) -> str:
    return _identifier(LAB_DATASET, "release", day.isoformat(), sequence)[:40]


def _at(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=timezone.utc)


def lab_history_events(end_day: date) -> tuple[HistoricalEvent, ...]:
    """Return the small deterministic lab dataset ending on a UTC day."""
    first_day = end_day - timedelta(days=6)
    second_day = end_day - timedelta(days=5)
    failure_day = end_day - timedelta(days=3)
    final_deployment_day = end_day - timedelta(days=2)
    incident_id = f"lab-incident-{failure_day.isoformat()}"
    dataset_metadata = {"dataset": LAB_DATASET}

    definitions = (
        (
            "deployment_succeeded",
            _at(first_day, 10),
            _release_sha(first_day, 1),
            "succeeded",
            18 * 60,
            "argocd",
            dataset_metadata,
        ),
        (
            "deployment_succeeded",
            _at(second_day, 14),
            _release_sha(second_day, 1),
            "succeeded",
            14 * 60,
            "argocd",
            dataset_metadata,
        ),
        (
            "deployment_failed",
            _at(failure_day, 9),
            _release_sha(failure_day, 1),
            "failed",
            None,
            "argocd",
            dataset_metadata,
        ),
        (
            "incident_started",
            _at(failure_day, 9, 5),
            _release_sha(failure_day, 1),
            "active",
            None,
            "monitoring",
            {**dataset_metadata, "incident_id": incident_id},
        ),
        (
            "service_restored",
            _at(failure_day, 9, 25),
            _release_sha(failure_day, 1),
            "restored",
            None,
            "monitoring",
            {**dataset_metadata, "incident_id": incident_id},
        ),
        (
            "deployment_succeeded",
            _at(final_deployment_day, 16),
            _release_sha(final_deployment_day, 1),
            "succeeded",
            11 * 60,
            "argocd",
            dataset_metadata,
        ),
    )
    return tuple(
        HistoricalEvent(
            event_id=_identifier(
                LAB_DATASET,
                event_type,
                occurred_at.isoformat(),
                release_sha,
            ),
            event_type=event_type,
            occurred_at=occurred_at,
            release_sha=release_sha,
            environment="m-devops-dashboard",
            source=source,
            status=status,
            duration_seconds=duration_seconds,
            synthetic=True,
            metadata=metadata,
        )
        for (
            event_type,
            occurred_at,
            release_sha,
            status,
            duration_seconds,
            source,
            metadata,
        ) in definitions
    )


def validate_database_path(database_path: Path) -> Path:
    """Reject paths that are ambiguous or unsafe for an additive seed."""
    if database_path.suffix.lower() != ".db":
        raise ValueError("Seed database path must identify a .db file.")
    if database_path.exists() and (
        database_path.is_dir() or database_path.is_symlink()
    ):
        raise ValueError("Seed database path must be a regular file.")
    return database_path


def seed_lab_history(database_path: Path, end_day: date) -> tuple[int, int]:
    """Add the deterministic lab dataset without changing existing rows."""
    safe_path = validate_database_path(database_path)
    inserted = sum(
        insert_event(event, safe_path)
        for event in lab_history_events(end_day)
    )
    total = len(lab_history_events(end_day))
    return inserted, total - inserted


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add explicit synthetic 7-day dashboard lab telemetry.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=history_database_path(),
        help="SQLite database path (defaults to DASHBOARD_HISTORY_DB_PATH).",
    )
    parser.add_argument(
        "--end-date",
        type=date.fromisoformat,
        default=datetime.now(timezone.utc).date(),
        help="Final UTC calendar day in YYYY-MM-DD format.",
    )
    return parser.parse_args()


def main() -> None:
    args = _arguments()
    inserted, existing = seed_lab_history(args.database, args.end_date)
    print(f"Lab telemetry inserted: {inserted}")
    print(f"Lab telemetry already present: {existing}")
    print(f"Database: {args.database}")


if __name__ == "__main__":
    main()
