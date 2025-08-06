from typing import List, Optional

from lib.get_file_creation_date.domain.create_date_result import (
    GetFileCreationDateResult,
)
from lib.get_file_creation_date.get_oldest_entry import get_oldest_entry
from lib.get_file_creation_date.providers.file_creation_date_provider import (
    FileCreationDateProvider,
)
from lib.get_file_creation_date.providers.filename.filename import (
    FilenameFileCreationDateProvider,
)
from lib.get_file_creation_date.providers.hachoir.hachoir import (
    HachoirFileCreationDateProvider,
)
from lib.get_file_creation_date.providers.windows_shell.windows_shell import (
    WindowsShellFileCreationDateProvider,
)

# A list of all available file creation date providers.
_PROVIDERS: List[FileCreationDateProvider] = [
    FilenameFileCreationDateProvider(),
    HachoirFileCreationDateProvider(),
    WindowsShellFileCreationDateProvider(),
]

# A list of providers that are currently available on the system.
_PROVIDERS_AVAILABLE = [provider for provider in _PROVIDERS if provider.is_available()]


def get_file_creation_date(file_path: str) -> Optional[GetFileCreationDateResult]:
    """
    Gets the creation date of a file using a variety of providers.

    This function iterates through a list of available providers and returns the
    oldest creation date found among them.

    Args:
        file_path: The path to the file.

    Returns:
        A GetFileCreationDateResult object containing the oldest creation date
        and the name of the provider that found it, or None if no creation date
        could be found.
    """
    entries = [
        provider.get_file_creation_date(file_path)
        for provider in _PROVIDERS_AVAILABLE
        if provider.supports_file(file_path)
    ]
    return get_oldest_entry([entry for entry in entries if entry is not None])
