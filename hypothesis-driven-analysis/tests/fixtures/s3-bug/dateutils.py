"""Date parsing helpers."""

from datetime import datetime


def parse_date(value: str) -> datetime:
    """Parse an ISO-8601 date string into a datetime."""
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
