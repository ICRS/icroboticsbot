__all__ = [
    "UserNote"
]
from dataclasses import dataclass
import datetime


@dataclass
class UserNote:
    uid: int
    shortcode: str
    note: str
    created: datetime.datetime

    @property
    def created_time(self):
        return datetime.datetime.fromisoformat(self.created)
