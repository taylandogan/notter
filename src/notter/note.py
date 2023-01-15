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
    ) -> None:
        self.note_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.timestamp = str(datetime.now())
        self.filepath = filepath
        self.line = line
        self.type = type

    def json(self) -> Dict[str, Any]:
        return {
            "note_id": self.note_id,
            "type": self.type.value,
            "username": self.username,
            "email": self.email,
            "filepath": self.filepath,
            "line": self.line,
            "timestamp": self.timestamp,
        }


class Content:
    def __init__(self, text: str) -> None:
        self.text = text


class NoteWithContent:
    def __init__(self, note: Note, content: Content) -> None:
        self.note = note
        self.content = content
