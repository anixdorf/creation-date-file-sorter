from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Tuple

from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult


class FileCreationDateProvider(ABC):

    @abstractmethod
    def get_file_creation_date(self, file_path: str) -> Optional[GetFileCreationDateResult]:
        pass
