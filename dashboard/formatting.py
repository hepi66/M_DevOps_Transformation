from datetime import datetime


def format_dashboard_timestamp(timestamp: datetime | str | None) -> str:
    """Format a timestamp using the dashboard's compact display standard."""
    if not timestamp:
        return "-- --- --:--:--"

    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError):
            return "-- --- --:--:--"

    return timestamp.astimezone().strftime("%d %b %H:%M:%S")
