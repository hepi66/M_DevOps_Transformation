from datetime import datetime

MINIMUM_DASHBOARD_YEAR = 1970
MAXIMUM_DASHBOARD_YEAR = 9998
DASHBOARD_TIMESTAMP_FALLBACK = "-- --- --:--:--"


def parse_dashboard_timestamp(timestamp: object) -> datetime | None:
    """Parse one timestamp while rejecting sentinel and unsafe date ranges."""
    if isinstance(timestamp, datetime):
        parsed = timestamp
    elif isinstance(timestamp, str) and timestamp:
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    else:
        return None

    if not MINIMUM_DASHBOARD_YEAR <= parsed.year <= MAXIMUM_DASHBOARD_YEAR:
        return None
    return parsed


def normalize_dashboard_timestamp(timestamp: object) -> str | None:
    """Return a safe ISO timestamp for models and operational events."""
    parsed = parse_dashboard_timestamp(timestamp)
    return parsed.isoformat() if parsed is not None else None


def format_dashboard_timestamp(timestamp: object) -> str:
    """Format a timestamp without allowing malformed data to break the UI."""
    parsed = parse_dashboard_timestamp(timestamp)
    if parsed is None:
        return DASHBOARD_TIMESTAMP_FALLBACK

    try:
        return parsed.astimezone().strftime("%d %b %H:%M:%S")
    except (OSError, OverflowError, ValueError):
        return DASHBOARD_TIMESTAMP_FALLBACK
