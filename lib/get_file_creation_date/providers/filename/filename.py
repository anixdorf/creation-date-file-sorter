import logging
from pathlib import Path
from typing import Optional

from lib.dateparser.dateparser import parse_date
from lib.get_file_creation_date.domain.create_date_result import (
    GetFileCreationDateResult,
)
from lib.get_file_creation_date.providers.file_creation_date_provider import (
    FileCreationDateProvider,
)


class FilenameFileCreationDateProvider(FileCreationDateProvider):
    def __init__(self):
        """Initialize the filename provider."""
        super().__init__()
        self.logger = logging.getLogger(__name__.split(".")[-1])

    def is_available(self) -> bool:
        """Check if filename extraction is available."""
        return True  # Always available

    def supports_file(self, file_path: str) -> bool:
        """Check if this provider supports the given file."""
        return True  # Can analyze any filename

    def get_file_creation_date(
        self, file_path: str
    ) -> Optional[GetFileCreationDateResult]:
        """Extract creation date from filename patterns."""
        parsed_date = parse_date(Path(file_path).name)
        if parsed_date:
            self.logger.debug(f"Found creation date: {parsed_date}")
        else:
            self.logger.debug(f"No creation date found in filename")

        return (
            GetFileCreationDateResult(creation_date=parsed_date, provider="filename")
            if parsed_date
            else None
        )
