from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dashboard.lifecycle import PipelineRun

LOGGER = logging.getLogger(__name__)
DEFAULT_HISTORY_DB_PATH = Path(".data/dashboard_history.db")
HISTORY_DB_ENVIRONMENT_VARIABLE = "DASHBOARD_HISTORY_DB_PATH"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class HistoricalEvent:
    """One normalized, persistent operational event."""

    event_id: str
    event_type: str
    occurred_at: datetime
    release_sha: str | None
    environment: str
    source: str
    status: str | None = None
    duration_seconds: int | None = None
    synthetic: bool = False
    metadata: dict[str, Any] | None = None


def history_database_path() -> Path:
    """Return the configured history database without opening it."""
    return Path(
        os.environ.get(
            HISTORY_DB_ENVIRONMENT_VARIABLE,
            str(DEFAULT_HISTORY_DB_PATH),
        )
    )


def _utc_timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Historical event timestamps must be timezone-aware.")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_utc_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )


@contextmanager
def _connection(database_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    path = database_path or history_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("PRAGMA journal_mode = WAL")
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_schema(database_path: Path | None = None) -> None:
    """Initialize the versioned telemetry schema on an empty database."""
    with _connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO schema_version(version) VALUES (?)",
            (SCHEMA_VERSION,),
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS historical_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                release_sha TEXT,
                environment TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT,
                duration_seconds INTEGER CHECK (
                    duration_seconds IS NULL OR duration_seconds >= 0
                ),
                synthetic INTEGER NOT NULL DEFAULT 0 CHECK (synthetic IN (0, 1)),
                metadata_json TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_historical_events_occurred_at
            ON historical_events(occurred_at)
            """
        )


def insert_event(
    event: HistoricalEvent,
    database_path: Path | None = None,
) -> bool:
    """Insert one event idempotently and return whether a row was created."""
    initialize_schema(database_path)
    metadata_json = (
        json.dumps(event.metadata, sort_keys=True, separators=(",", ":"))
        if event.metadata is not None
        else None
    )
    with _connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO historical_events (
                event_id,
                event_type,
                occurred_at,
                release_sha,
                environment,
                source,
                status,
                duration_seconds,
                synthetic,
                metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.event_type,
                _utc_timestamp(event.occurred_at),
                event.release_sha,
                event.environment,
                event.source,
                event.status,
                event.duration_seconds,
                int(event.synthetic),
                metadata_json,
            ),
        )
        return cursor.rowcount == 1


def _event_from_row(row: sqlite3.Row) -> HistoricalEvent:
    metadata = json.loads(row["metadata_json"]) if row["metadata_json"] else None
    return HistoricalEvent(
        event_id=row["event_id"],
        event_type=row["event_type"],
        occurred_at=_parse_utc_timestamp(row["occurred_at"]),
        release_sha=row["release_sha"],
        environment=row["environment"],
        source=row["source"],
        status=row["status"],
        duration_seconds=row["duration_seconds"],
        synthetic=bool(row["synthetic"]),
        metadata=metadata,
    )


def get_events_between(
    start: datetime,
    end: datetime,
    database_path: Path | None = None,
) -> tuple[HistoricalEvent, ...]:
    """Return events in the half-open UTC range [start, end)."""
    initialize_schema(database_path)
    with _connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM historical_events
            WHERE occurred_at >= ? AND occurred_at < ?
            ORDER BY occurred_at ASC, event_id ASC
            """,
            (_utc_timestamp(start), _utc_timestamp(end)),
        ).fetchall()
    return tuple(_event_from_row(row) for row in rows)


def get_events_since(
    start: datetime,
    database_path: Path | None = None,
) -> tuple[HistoricalEvent, ...]:
    """Return events from a UTC instant through the newest stored event."""
    initialize_schema(database_path)
    with _connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM historical_events
            WHERE occurred_at >= ?
            ORDER BY occurred_at ASC, event_id ASC
            """,
            (_utc_timestamp(start),),
        ).fetchall()
    return tuple(_event_from_row(row) for row in rows)


def get_recent_events(
    limit: int = 100,
    database_path: Path | None = None,
) -> tuple[HistoricalEvent, ...]:
    """Return the newest bounded event set without exposing SQL."""
    if limit <= 0:
        return ()
    initialize_schema(database_path)
    with _connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM historical_events
            ORDER BY occurred_at DESC, event_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return tuple(_event_from_row(row) for row in rows)


def count_events(database_path: Path | None = None) -> int:
    """Return the number of normalized historical events."""
    initialize_schema(database_path)
    with _connection(database_path) as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS event_count FROM historical_events"
        ).fetchone()
    return int(row["event_count"] if row else 0)


def _immutable_release_sha(pipeline_run: PipelineRun) -> str | None:
    tag = str(pipeline_run.kubernetes.image_tag or "").lower()
    if len(tag) != 40 or any(character not in "0123456789abcdef" for character in tag):
        return None
    return tag


def _event_id(
    event_type: str,
    release_sha: str,
    occurred_at: datetime,
    source: str,
    provider_identity: str | None,
) -> str:
    identity = "|".join(
        (
            event_type,
            release_sha,
            _utc_timestamp(occurred_at),
            source,
            provider_identity or "",
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def events_from_pipeline_run(
    pipeline_run: PipelineRun,
) -> tuple[HistoricalEvent, ...]:
    """Project only lifecycle events established by normalized evidence."""
    release_sha = _immutable_release_sha(pipeline_run)
    if release_sha is None:
        return ()

    argocd = pipeline_run.argocd
    kubernetes = pipeline_run.kubernetes
    environment = kubernetes.namespace or argocd.namespace or "local-kubernetes"
    metadata = {
        key: value
        for key, value in {
            "argocd_application": argocd.application,
            "kubernetes_deployment": kubernetes.deployment,
            "image_digest": kubernetes.image_digest,
        }.items()
        if value
    }
    operation_phase = str(argocd.operation_phase or "").lower()
    replicas_ready = bool(
        kubernetes.desired_replicas
        and kubernetes.ready_replicas is not None
        and kubernetes.ready_replicas >= kubernetes.desired_replicas
    )
    if (
        argocd.operation_at
        and operation_phase == "succeeded"
        and str(argocd.sync_status or "").lower() == "synced"
        and str(argocd.health_status or "").lower() == "healthy"
        and kubernetes.status == "completed"
        and replicas_ready
    ):
        return (
            HistoricalEvent(
                event_id=_event_id(
                    "deployment_succeeded",
                    release_sha,
                    argocd.operation_at,
                    "argocd",
                    argocd.application,
                ),
                event_type="deployment_succeeded",
                occurred_at=argocd.operation_at,
                release_sha=release_sha,
                environment=environment,
                source="argocd",
                status="succeeded",
                duration_seconds=pipeline_run.lead_time_seconds,
                metadata=metadata or None,
            ),
        )
    if argocd.operation_at and operation_phase in {"failed", "error"}:
        return (
            HistoricalEvent(
                event_id=_event_id(
                    "deployment_failed",
                    release_sha,
                    argocd.operation_at,
                    "argocd",
                    argocd.application,
                ),
                event_type="deployment_failed",
                occurred_at=argocd.operation_at,
                release_sha=release_sha,
                environment=environment,
                source="argocd",
                status="failed",
                metadata=metadata or None,
            ),
        )
    return ()


def record_pipeline_events(
    pipeline_run: PipelineRun,
    database_path: Path | None = None,
) -> int:
    """Persist newly observed lifecycle events and return the insert count."""
    return sum(
        insert_event(event, database_path)
        for event in events_from_pipeline_run(pipeline_run)
    )


def record_pipeline_events_safely(pipeline_run: PipelineRun) -> bool:
    """Record history without allowing persistence to break live monitoring."""
    try:
        record_pipeline_events(pipeline_run)
    except Exception as error:  # noqa: BLE001 - history cannot break live state
        LOGGER.warning(
            "Historical telemetry unavailable: %s.",
            type(error).__name__,
        )
        return False
    return True
