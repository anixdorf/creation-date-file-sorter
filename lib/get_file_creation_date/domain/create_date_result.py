from dataclasses import dataclass

import datetime as datetime


@dataclass
class GetFileCreationDateResult:
    method: str
    creation_date: datetime
