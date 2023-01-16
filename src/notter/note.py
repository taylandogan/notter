from typing import Any, Dict
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
        type: NoteType = NoteType.NOTE,
        note_id: str = None,
        timestamp: str = None,
    ) -> None:
        self.username = username
        self.email = email
        self.filepath = filepath
        self.line = line
        self.type = type
        self.note_id = note_id if note_id else str(uuid.uuid4())
        self.timestamp = timestamp if timestamp else str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))


class Content:
    def __init__(self, text: str) -> None:
        self.text = text


class NoteWithContent:
    def __init__(self, note: Note, content: Content) -> None:
        self.note = note
        self.content = content

    def __str__(self) -> str:
        return f"{self.content.text} - {self.note.username} / {self.note.timestamp}"
