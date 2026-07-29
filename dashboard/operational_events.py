from dataclasses import dataclass
from datetime import timezone
from typing import Literal

from dashboard.formatting import parse_dashboard_timestamp

EventClassification = Literal[
    "lifecycle",
    "status",
    "metadata",
    "warning",
    "failure",
    "information",
]


@dataclass(frozen=True)
class OperationalEvent:
    """Represent one immutable operational timeline entry."""

    timestamp: str | None
    source_identifier: str
    source_abbreviation: str
    category: str
    status: str
    icon: str
    message: str
    classification: EventClassification = "information"
    detail: str | None = None
    external_url: str | None = None
    order: int = 0
    event_id: str | None = None


def order_operational_events(
    events: list[OperationalEvent],
) -> list[OperationalEvent]:
    """Remove duplicates and order events newest first."""
    unique_events: list[OperationalEvent] = []
    seen: set[object] = set()

    for event in events:
        identity = event.event_id or (
            event.timestamp,
            event.source_identifier,
            event.category,
            event.status,
            event.message,
            event.detail,
            event.external_url,
        )
        if identity in seen:
            continue
        seen.add(identity)
        unique_events.append(event)

    source_order = {
        "GI": 0,
        "GH": 1,
        "CI": 2,
        "DB": 3,
        "CR": 4,
        "CD": 5,
        "K8": 6,
    }

    def sort_key(event: OperationalEvent) -> tuple[float, int, int, str]:
        timestamp = parse_dashboard_timestamp(event.timestamp)
        if timestamp is not None:
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            try:
                epoch = timestamp.timestamp()
            except (OSError, OverflowError, ValueError):
                epoch = float("inf")
        else:
            epoch = float("inf")

        timestamp_order = -epoch if epoch != float("inf") else epoch
        return (
            timestamp_order,
            source_order.get(event.source_abbreviation, 99),
            event.order,
            event.event_id or "",
        )

    return sorted(unique_events, key=sort_key)
