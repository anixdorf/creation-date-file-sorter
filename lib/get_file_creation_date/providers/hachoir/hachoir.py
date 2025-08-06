import logging
from datetime import datetime
from typing import Optional

try:
    from hachoir.parser import createParser
    from hachoir.metadata import extractMetadata
    from hachoir.core import config as hachoir_config

    HACHOIR_AVAILABLE = True
except ImportError:
    HACHOIR_AVAILABLE = False

from lib.dateparser.dateparser import parse_date
from lib.get_file_creation_date.domain.create_date_result import (
    GetFileCreationDateResult,
)
from lib.get_file_creation_date.providers.file_creation_date_provider import (
    FileCreationDateProvider,
)


class HachoirFileCreationDateProvider(FileCreationDateProvider):
    """
    Extract creation dates using Hachoir metadata library.

    Hachoir can extract metadata from many file formats including:
    - Images (JPEG, PNG, TIFF, etc.)
    - Videos (MP4, AVI, MOV, etc.)
    - Audio (MP3, FLAC, etc.)
    - Documents (PDF, etc.)
    """

    def __init__(self):
        """Initialize the Hachoir provider."""
        super().__init__()
        self.logger = logging.getLogger(__name__.split(".")[-1])

        if not HACHOIR_AVAILABLE:
            self.logger.warning(
                "Hachoir not available. Install with: pip install hachoir"
            )
        else:
            hachoir_config.quiet = True

    def is_available(self) -> bool:
        """Check if Hachoir extraction is available."""
        return HACHOIR_AVAILABLE

    def supports_file(self, file_path: str) -> bool:
        """Check if this provider supports the given file."""
        return True

    def get_file_creation_date(
        self, file_path: str
    ) -> Optional[GetFileCreationDateResult]:
        """Extract creation date using Hachoir metadata."""
        try:
            parser = createParser(file_path)
            if not parser:
                self.logger.debug(f"Hachoir could not create parser")
                return None

            metadata = extractMetadata(parser)
            if not metadata:
                self.logger.debug(f"Hachoir could not extract metadata")
                return None

            creation_date = self._find_creation_date(metadata)
            if creation_date:
                self.logger.debug(f"Found creation date: {creation_date}")

                return GetFileCreationDateResult(
                    creation_date=creation_date, provider=self.__class__.__name__
                )

            self.logger.debug(f"No creation date found in Hachoir metadata")
            return None

        except Exception as e:
            self.logger.debug(f"Hachoir extraction failed for {file_path}: {e}")
            return None

        finally:
            # Clean up parser
            if "parser" in locals() and parser:
                try:
                    parser.stream._input.close()
                except:
                    pass

    def _find_creation_date(self, metadata) -> Optional[datetime]:
        """Find creation date in Hachoir metadata."""
        date_fields = [
            # --- High Priority ---
            # Most reliable EXIF and common metadata tags for creation time.
            "date_time_original",  # (EXIF) The ideal tag for original image creation.
            "creation_date",  # A very common and explicit tag.
            "date_created",  # Clear and widely used.
            "created",  # Another common variant.
            # --- Medium Priority ---
            # Good for specific file types like video and audio.
            "recording_date",  # Specific to video/audio.
            "shotdate",  # (XMP) Explicitly for when a video was shot.
            # --- Low Priority (Last Resort) ---
            # These are often modification dates, but can be a fallback.
            "date_time",  # (EXIF) Often the modification date, use with caution.
            "modification_date",
            "last_modification",
        ]

        for field_name in date_fields:
            try:
                value = metadata.get(field_name)
                if value:
                    parsed_date = self._parse_metadata_date(value)
                    if parsed_date:
                        return parsed_date
            except Exception as e:
                self.logger.debug(f"Error accessing field '{field_name}': {e}")
                continue

        return None

    def _parse_metadata_date(self, value) -> Optional[datetime]:
        """Parse a date value from metadata."""
        if not value:
            return None

        date_str = str(value).strip()

        if not date_str:
            return None

        parsed_date = parse_date(date_str)
        if parsed_date:
            return parsed_date

        self.logger.debug(f"Could not parse metadata date: {date_str}")
        return None
