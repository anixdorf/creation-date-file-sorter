import re
import logging
from datetime import datetime
from typing import Optional

try:
    from dateutil import parser as dateutil_parser

    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False


class DateParser:
    """
    Enhanced date parser supporting multiple formats and patterns.
    """

    def __init__(self):
        """Initialize the enhanced date parser."""
        self.logger = logging.getLogger(__name__)

        if not DATEUTIL_AVAILABLE:
            self.logger.warning(
                "dateutil not available. Install with: pip install python-dateutil"
            )

        # Define regex patterns with their corresponding format strings
        self.patterns = [
            # YYYY-MM-DD HH:MM:SS
            (
                r"(20[0-2][0-9]-[0-1][0-9]-[0-3][0-9])[T ]([0-2][0-9]:[0-5][0-9]:[0-5][0-9])",
                "%Y-%m-%d %H:%M:%S",
            ),
            # YYYYMMDD_HHMMSS
            (
                r"(20[0-2][0-9][0-1][0-9][0-3][0-9])_([0-2][0-9][0-5][0-9][0-5][0-9])",
                "%Y%m%d_%H%M%S",
            ),
            # Date-only formats (YYYYMMDD, YYYY-MM-DD, etc.)
            (r"\b(20[0-2][0-9][0-1][0-9][0-3][0-9])\b", "%Y%m%d"),
            (r"\b(20[0-2][0-9]-[0-1][0-9]-[0-3][0-9])\b", "%Y-%m-%d"),
            (r"(20[0-2][0-9]_[0-1][0-9]_[0-3][0-9])", "%Y_%m_%d"),
            (r"\b(20[0-2][0-9]\.[0-1][0-9]\.[0-3][0-9])\b", "%Y.%m.%d"),
            # European formats (DD.MM.YYYY, etc.)
            (r"\b([0-3][0-9]\.[0-1][0-9]\.20[0-2][0-9])\b", "%d.%m.%Y"),
            (r"\b([0-3][0-9]-[0-1][0-9]-20[0-2][0-9])\b", "%d-%m-%Y"),
            # Common file naming patterns
            (r"IMG[_-]?(20[0-2][0-9][0-1][0-9][0-3][0-9])", "%Y%m%d"),
            (r"VID[_-]?(20[0-2][0-9][0-1][0-9][0-3][0-9])", "%Y%m%d"),
            (r"Screenshot.*?(20[0-2][0-9]-[0-1][0-9]-[0-3][0-9])", "%Y-%m-%d"),
        ]

        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), fmt) for pattern, fmt in self.patterns
        ]

    def parse(self, text: str) -> Optional[datetime]:
        """
        Parse date from text using multiple strategies.
        """
        if not text:
            return None

        # Strategy 1: Try regex patterns
        result = self._parse_with_patterns(text)
        if result:
            return result

        # Strategy 2: Try dateutil parser (if available)
        if DATEUTIL_AVAILABLE:
            result = self._parse_with_dateutil(text)
            if result:
                return result

        return None

    def _parse_with_patterns(self, text: str) -> Optional[datetime]:
        """Parse using predefined regex patterns."""
        for pattern, fmt in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                try:
                    # Handle combined date and time
                    if len(match.groups()) > 1:
                        date_str = " ".join(match.groups())
                    else:
                        date_str = match.group(1)

                    # Handle special case where format needs underscore
                    if "_" in fmt and " " in date_str:
                        date_str = date_str.replace(" ", "_")

                    parsed_date = datetime.strptime(date_str, fmt)

                    if 1980 <= parsed_date.year <= 2050:
                        self.logger.debug(
                            f"Parsed '{date_str}' with pattern '{pattern.pattern}'"
                        )
                        return parsed_date
                except (ValueError, IndexError):
                    continue
        return None

    def _parse_with_dateutil(self, text: str) -> Optional[datetime]:
        """Parse using dateutil's flexible parser."""
        try:
            from dateutil import tz
            from dateutil.parser import parse as dateutil_parse_func

            # Define tzinfos for "MTS" to use the local system timezone
            tzinfos = {"MTS": tz.tzlocal()}

            # Use fuzzy parsing to find a date within the string
            parsed_date, fuzzy_tokens = dateutil_parse_func(
                text, fuzzy_with_tokens=True, tzinfos=tzinfos
            )

            # Reconstruct the string that was actually parsed
            parsed_string = text
            for token in fuzzy_tokens:
                parsed_string = parsed_string.replace(token, "")
            parsed_string = parsed_string.strip().lower()

            # Check if month and day were likely present in the parsed string
            month_str = str(parsed_date.month)
            month_name_short = parsed_date.strftime("%b").lower()
            month_name_full = parsed_date.strftime("%B").lower()

            month_present = (
                month_str in parsed_string
                or month_name_short in parsed_string
                or month_name_full in parsed_string
            )
            day_present = str(parsed_date.day) in parsed_string

            if month_present and day_present:
                if 1980 <= parsed_date.year <= 2050:
                    self.logger.debug(f"Parsed '{text}' using dateutil")
                    return parsed_date

        except (ValueError, OverflowError, TypeError):
            pass
        return None


_default_parser = DateParser()


def parse_date(text: str) -> Optional[datetime]:
    """
    Parses a date from a string using the default EnhancedDateParser instance.
    """
    return _default_parser.parse(text)
