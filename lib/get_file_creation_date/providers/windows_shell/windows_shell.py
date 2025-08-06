import logging
import platform
from typing import Optional

try:
    from win32com.propsys import propsys
    from win32com.shell import shellcon
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False
    propsys = None
    shellcon = None

from lib.dateparser.dateparser import parse_date
from lib.get_file_creation_date.domain.create_date_result import (
    GetFileCreationDateResult,
)
from lib.get_file_creation_date.providers.file_creation_date_provider import (
    FileCreationDateProvider,
)


class WindowsShellFileCreationDateProvider(FileCreationDateProvider):
    PRIORITY_PROPERTIES = [
        "System.Photo.DateTaken",  # Highest priority for photos
        "System.DateAcquired",  # When file was acquired/downloaded
        "System.DateCreated",  # File system creation date
        "System.DateModified",  # File system modification date (fallback)
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__.split(".")[-1])

    def is_available(self) -> bool:
        """Check if Windows Shell extraction is available."""
        return platform.system() == "Windows" and WIN32COM_AVAILABLE

    def supports_file(self, file_path: str) -> bool:
        """Check if this provider supports the given file."""
        return True  # Can work on any file

    def get_file_creation_date(
        self, file_path: str
    ) -> Optional[GetFileCreationDateResult]:
        """Use modern Windows Property System with universal PKEYs"""
        if not self.is_available():
            return None
            
        try:
            # Get property store for the file
            prop_store = propsys.SHGetPropertyStoreFromParsingName(
                file_path, None, shellcon.GPS_DEFAULT, propsys.IID_IPropertyStore
            )

            # Try each property in priority order
            for prop_name in self.PRIORITY_PROPERTIES:
                try:
                    # Get the property key from canonical name
                    prop_key = propsys.PSGetPropertyKeyFromName(prop_name)

                    # Get the property value
                    prop_value = prop_store.GetValue(prop_key)

                    if prop_value and prop_value.GetValue():
                        # Convert to string and parse date
                        value_str = str(prop_value.GetValue())
                        parsed_date = parse_date(value_str)

                        if parsed_date:
                            self.logger.debug(
                                f"Found creation date: {prop_name} = {parsed_date}"
                            )
                            return GetFileCreationDateResult(
                                provider="windows_shell",
                                provider_info=prop_name,
                                creation_date=parsed_date,
                            )

                except Exception as e:
                    self.logger.debug(f"Property {prop_name} not available: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Property system access failed for {file_path}: {e}")

        return None
