from datetime import datetime
from unittest import TestCase

from lib.get_file_creation_date.create_date_result import GetFileCreationDateResult
from lib.get_file_creation_date.get_oldest_entry import get_oldest_entry


class TestGetOldestEntry(TestCase):
    def test_empty_list(self):
        # Given
        entries = []

        # When
        result = get_oldest_entry(entries)

        # Then
        assert(result is None)

    def test_with_entries_ascending_order(self):
        # Given
        entries = [
            GetFileCreationDateResult("A", datetime(2023, 1, 1, 0, 0)),
            GetFileCreationDateResult("B", datetime(2023, 1, 2, 0, 0)),
            GetFileCreationDateResult("C", datetime(2023, 1, 3, 0, 0))
        ]

        # When
        result = get_oldest_entry(entries)

        # Then
        assert(result.method == "A")
        assert(result.creation_date == datetime(2023, 1, 1, 0, 0))

    def test_with_entries_descending_order(self):
        # Given
        entries = [
            GetFileCreationDateResult("C", datetime(2023, 1, 3, 0, 0)),
            GetFileCreationDateResult("B", datetime(2023, 1, 2, 0, 0)),
            GetFileCreationDateResult("A", datetime(2023, 1, 1, 0, 0))
        ]

        # When
        result = get_oldest_entry(entries)

        # Then
        assert(result.method == "A")
        assert(result.creation_date == datetime(2023, 1, 1, 0, 0))

    def test_with_entries_unordered(self):
        # Given
        entries = [
            GetFileCreationDateResult("C", datetime(2023, 1, 3, 0, 0)),
            GetFileCreationDateResult("A", datetime(2023, 1, 1, 0, 0)),
            GetFileCreationDateResult("B", datetime(2023, 1, 2, 0, 0))
        ]

        # When
        result = get_oldest_entry(entries)

        # Then
        assert(result.method == "A")
        assert(result.creation_date == datetime(2023, 1, 1, 0, 0))
