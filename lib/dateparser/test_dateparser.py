from datetime import datetime
from unittest import TestCase

from lib.dateparser.dateparser import parse_date


class TestParseDate(TestCase):
    def test_variant_1(self):
        text = "_abc-20160611-."  # When
        result = parse_date(text)  # Given
        assert(result == datetime(2016, 6, 11, 0, 0))  # Then

    def test_variant_2(self):
        text = "_abc-2016-06-11-."  # When
        result = parse_date(text)  # Given
        assert(result == datetime(2016, 6, 11, 0, 0))  # Then

    def test_variant_3(self):
        text = "_abc-20-12-05-."  # When
        result = parse_date(text)  # Given
        assert(result == datetime(2020, 12, 5, 0, 0))  # Then

    def test_variant_4(self):
        text = "_abc-30.04.2020-."  # When
        result = parse_date(text)  # Given
        assert(result == datetime(2020, 4, 30, 0, 0))  # Then
