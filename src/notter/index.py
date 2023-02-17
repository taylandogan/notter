import json
from typing import Dict, Optional, Set

from notter.exceptions import NoteAlreadyExists, NoteNotFound
from notter.model import Note
from notter.utils import CustomEncoder, persist_index_after

Line = str
FilePath = str
NoteDict = Dict[FilePath, Dict[Line, Note]]


class NoteIndex:
    def __init__(self, index_path: str) -> None:
        self.idx: NoteDict = {}
        self.idx_path = index_path

    def init_index(self, index_path: str) -> None:
        with open(index_path, "w+") as idx_file:
            json.dump(self.idx, idx_file, cls=CustomEncoder, indent=4)

    def load_index(self, index_path: str) -> None:
        with open(index_path, "r") as file:
            self.idx = json.loads(file.read())

    def seek(self, filepath: str, line: str) -> bool:
        file_entry = self.idx.get(filepath)
        if not file_entry:
            return False

        note_entry = file_entry.get(line)
        if not note_entry:
            return False

        return True

    def fetch(self, filepath: str, line: str) -> Optional[Note]:
        note_exists = self.seek(filepath, line)
        if not note_exists:
            raise NoteNotFound

        return self.idx[filepath][line]

    def summarize(self) -> Set[str]:
        entry_set: Set[str] = set()
        for filepath, note_dict in self.idx.items():
            for line in note_dict.keys():
                entry_set.add(f"{filepath}:{line}")

        return entry_set

    @persist_index_after
    def store(self, note: Note, update: bool = False) -> None:
        note_exists = self.seek(note.filepath, str(note.line))
        if not update and note_exists:
            raise NoteAlreadyExists

        self.idx[note.filepath] = self.idx.get(note.filepath, {})
        self.idx[note.filepath][str(note.line)] = note

    @persist_index_after
    def clean(self, filepath: str, line: str) -> Optional[Note]:
        note = self.fetch(filepath, line)
        file_entry = self.idx[filepath]
        file_entry.pop(line)

        # Get rid of file entry if it has no keys inside
        if not file_entry:
            self.idx.pop(filepath)

        return note
