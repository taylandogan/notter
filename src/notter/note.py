from time import time
import uuid

from datetime import datetime
from enum import Enum


class NoteType(str, Enum):
    NOTE = "NOTE"
    TODO = "TODO"


class Note:
    def __init__(
        self,
        username: str,
        email: str,
        filepath: str,
        line: int,
        text: str,
        type: NoteType = NoteType.NOTE,
    ):
        self.note_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.timestamp = datetime.now()
        self.filepath = filepath
        self.line = line
        self.text = text
        self.type = type
