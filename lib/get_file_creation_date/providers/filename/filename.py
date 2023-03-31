from pathlib import Path
from typing import Optional

from lib.dateparser.dateparser import parse_date
from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult
from lib.get_file_creation_date.providers.file_creation_date_provider import FileCreationDateProvider


class FilenameFileCreationDateProvider(FileCreationDateProvider):
    def get_file_creation_date(self, file_path: str) -> Optional[GetFileCreationDateResult]:
        parsed_date = parse_date(Path(file_path).name)
        return GetFileCreationDateResult(method="Dateiname", creation_date=parsed_date) if parsed_date else None
