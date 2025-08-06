from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Tuple

from lib.get_file_creation_date.domain.create_date_result import (
    GetFileCreationDateResult,
)


class FileCreationDateProvider(ABC):
    """
    Abstract base class for date extraction providers.

    All providers should inherit from this class and implement the required methods.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this provider is available on the current system.

        Returns:
            bool: True if the provider can be used, False otherwise.
        """
        pass

    @abstractmethod
    def supports_file(self, file_path: str) -> bool:
        """
        Check if this provider supports the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            bool: True if this provider can handle the file, False otherwise.
        """
        pass

    @abstractmethod
    def get_file_creation_date(
        self, file_path: str
    ) -> Optional[GetFileCreationDateResult]:
        """
        Extract the creation date from the given file.

        Args:
            file_path: Path to the file to analyze.

        Returns:
            Optional[GetFileCreationDateResult]: The extracted date information,
            or None if no date could be extracted.
        """
        pass

    def __str__(self) -> str:
        """String representation of the provider."""
        return self.__class__.__name__

    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(available={self.is_available()})"
