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
        id: str = None,
        created_at: str = None,
        updated_at: str = None,
    ) -> None:
        self.username = username
        self.email = email
        self.filepath = filepath
        self.line = line
        self.type = type
        self.id = id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()


class Content:
    def __init__(self, text: str) -> None:
        self.text = text


class NoteWithContent:
    def __init__(self, note: Note, content: Content) -> None:
        self.note = note
        self.content = content

    def __str__(self) -> str:
        return f"{self.content.text} - {self.note.username} / {self.note.updated_at}"


class Comment:
    def __init__(self, filepath: str, text: str, line: int, multiline: bool) -> None:
        self.filepath = filepath
        self.text = text
        self.line = line
        self.multiline = multiline

    def __str__(self) -> str:
        return f"{self.filepath}:{self.line} - {self.text}"
