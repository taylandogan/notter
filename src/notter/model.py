from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NoteType(str, Enum):
    NOTE = "NOTE"
    TODO = "TODO"


# TODO: Add input validation, max number of characters for each field
@dataclass
class Note:
    id: str
    filepath: str
    line: int
    type: NoteType = NoteType.NOTE
    created_at: str | None = datetime.now().isoformat()
    updated_at: str | None = datetime.now().isoformat()


@dataclass
class Content:
    text: str


@dataclass
class NoteWithContent:
    note: Note
    content: Content

    def __str__(self) -> str:
        return f"{self.content.text} / {self.note.updated_at}"

    @property
    def location_id(self) -> str:
        return f"{self.note.filepath}:{self.note.line}"

    def to_dict(self) -> dict:
        return {
            "id": self.note.id,
            "filepath": self.note.filepath,
            "line": self.note.line,
            "type": self.note.type.value,
            "created_at": self.note.created_at,
            "updated_at": self.note.updated_at,
            "content": self.content.text,
        }

    # TODO: This is too ugly, find a better way to do this
    @staticmethod
    def from_db_row(row: tuple) -> "NoteWithContent":
        note = Note(
            id=row[0],
            filepath=row[1],
            line=row[2],
            type=NoteType(row[3]),
            created_at=row[4],
            updated_at=row[5],
        )
        content = Content(text=row[6])
        return NoteWithContent(note, content)

    def to_db_row(self) -> tuple:
        return (
            self.note.id,
            self.note.filepath,
            self.note.line,
            self.note.type.value,
            self.note.created_at,
            self.note.updated_at,
            self.content.text,
        )


@dataclass
class Comment:
    filepath: str
    text: str
    line: int
    type: NoteType
    multiline: bool = False

    def __str__(self) -> str:
        return f"{self.filepath}:{self.line} - {self.text}"

    @property
    def location_id(self) -> str:
        return f"{self.filepath}:{self.line}"
