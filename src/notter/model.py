from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class NoteType(str, Enum):
    NOTE = "NOTE"
    TODO = "TODO"


# TODO: Add input validation, max number of characters for each field
@dataclass
class Note:
    id: str
    username: str
    email: str
    filepath: str
    line: int
    type: NoteType = NoteType.NOTE
    created_at: Optional[str] = datetime.now().isoformat()
    updated_at: Optional[str] = datetime.now().isoformat()


@dataclass
class Content:
    text: str


@dataclass
class NoteWithContent:
    note: Note
    content: Content

    def __str__(self) -> str:
        return f"{self.content.text} - {self.note.username} / {self.note.updated_at}"


@dataclass
class Comment:
    filepath: str
    text: str
    line: int
    type: NoteType
    multiline: bool = False

    def __str__(self) -> str:
        return f"{self.filepath}:{self.line} - {self.text}"
