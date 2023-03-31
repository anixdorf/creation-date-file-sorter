from typing import List, Optional, Tuple

from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult
from lib.get_file_creation_date.get_oldest_entry import get_oldest_entry
from lib.get_file_creation_date.providers.file_creation_date_provider import FileCreationDateProvider
from lib.get_file_creation_date.providers.filename.filename import FilenameFileCreationDateProvider
from lib.get_file_creation_date.providers.windows_shell.windows_shell import WindowsShellFileCreationDateProvider

_PROVIDERS: List[FileCreationDateProvider] = [
    WindowsShellFileCreationDateProvider(),
    FilenameFileCreationDateProvider()
]


def get_file_creation_date(file_path: str) -> Optional[GetFileCreationDateResult]:
    entries = [provider.get_file_creation_date(file_path) for provider in _PROVIDERS]
    return get_oldest_entry([entry for entry in entries if entry is not None])

