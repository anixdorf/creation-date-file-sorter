from typing import Optional, List

from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult


def get_oldest_entry(entries: List[GetFileCreationDateResult]) -> Optional[GetFileCreationDateResult]:
    entries.sort(key=lambda entry: entry.creation_date)
    return entries[0] if entries else None
