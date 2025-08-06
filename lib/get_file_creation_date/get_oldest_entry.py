from datetime import datetime, timezone
from typing import List, Optional

from lib.get_file_creation_date.domain.create_date_result import (
    GetFileCreationDateResult,
)


def _normalize_datetime(dt: datetime) -> datetime:
    """Normalize a datetime to be timezone-aware and in UTC."""
    if dt.tzinfo is None:
        # Assume naive datetime is in UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Convert aware datetime to UTC
        return dt.astimezone(timezone.utc)


def get_oldest_entry(
    entries: List[GetFileCreationDateResult],
) -> Optional[GetFileCreationDateResult]:
    """
    Finds the oldest entry from a list of GetFileCreationDateResult objects.

    Args:
        entries: A list of date extraction results.

    Returns:
        The result object with the earliest creation_date, or None if the list is empty.
    """
    if not entries:
        return None
    return min(entries, key=lambda entry: _normalize_datetime(entry.creation_date))
