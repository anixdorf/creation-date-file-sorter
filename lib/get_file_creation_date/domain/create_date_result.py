from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GetFileCreationDateResult:
    """
    A data class to store the result of a date extraction operation.
    """

    creation_date: datetime
    provider: str
    provider_info: Optional[str] = None
