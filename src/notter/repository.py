import json
from datetime import datetime
from pathlib import Path
from typing import Dict
from uuid import uuid4

import notter.constants as ncons
from notter.exceptions import NoteAlreadyExists, NoteNotFound
from notter.model import Content, Note, NoteWithContent
from notter.notter import Notter
from notter.utils import persist_index_after


class BaseRepository:
    def __init__(self, notter: Notter):
        raise NotImplementedError

    def create(self, note: Note):
        raise NotImplementedError

    def get(self) -> None:
        raise NotImplementedError

    def update(self) -> None:
        raise NotImplementedError

    def delete(self) -> None:
        raise NotImplementedError


class JsonFileRepository(BaseRepository):
    def __init__(self, notter: Notter) -> None:
        self.notter = notter
        self.idx: Dict[str, Note] = {}
        self.initialize_index_files()

    def initialize_index_files(self) -> None:
        idx_initialized = self.notter.get_config(ncons.IDX_INITIALIZED_FLAG)
        notter_path = Path(self.notter.get_config(ncons.PATH))
        note_idx_path = notter_path / ncons.NOTES_INDEX_FILENAME

        if not idx_initialized:
            with open(note_idx_path, "w+") as idx_file:
                idx_file.write(json.dumps(self.idx))
            self.notter.set_config(ncons.NOTES_INDEX_PATH, str(note_idx_path))
            self.notter.set_config(ncons.IDX_INITIALIZED_FLAG, True)
        else:
            with open(note_idx_path, "r") as file:
                self.idx = json.loads(file.read())

    @persist_index_after
    def create(self, note_with_content: NoteWithContent) -> None:
        idx_key = JsonFileRepository._get_index_key(note_with_content.note.filepath, note_with_content.note.line)
        if self.idx.get(idx_key, None):
            raise NoteAlreadyExists()

        # TODO: Make these two operations atomic
        # Write note content to a file
        with open(self._get_note_content_path(note_with_content.note.id), "w") as note_file:
            note_file.write(note_with_content.content.text)

        # Update the index
        # TODO: Handle possible JSON errors
        self.idx[idx_key] = note_with_content.note

    def read(self, filepath: str, line: int) -> NoteWithContent:
        idx_key = JsonFileRepository._get_index_key(filepath, line)
        entry = self.idx.get(idx_key, None)

        if not entry:
            raise NoteNotFound()

        # TODO: Handle possible JSON errors
        note = Note(**entry)
        with open(self._get_note_content_path(note.id), "r") as note_file:
            text = note_file.read()

        content = Content(text)
        return NoteWithContent(note, content)

    @persist_index_after
    def update(self, filepath: str, line: int, note_with_content: NoteWithContent) -> None:
        existing_note: NoteWithContent = self.read(filepath, line)
        existing_note.note.username = note_with_content.note.username
        existing_note.note.email = note_with_content.note.email
        existing_note.note.filepath = note_with_content.note.filepath
        existing_note.note.line = note_with_content.note.line
        existing_note.note.type = note_with_content.note.type
        existing_note.note.updated_at = datetime.now().isoformat()
        existing_note.content = note_with_content.content

        # TODO: Make these two operations atomic
        # Write note content to a file
        with open(self._get_note_content_path(existing_note.note.id), "w") as note_file:
            note_file.write(existing_note.content.text)

        # Update the index
        # TODO: Handle possible JSON errors
        idx_key = JsonFileRepository._get_index_key(filepath, line)
        self.idx[idx_key] = existing_note.note

    @persist_index_after
    def delete(self, filepath: str, line: int) -> None:
        idx_key = JsonFileRepository._get_index_key(filepath, line)
        entry = self.idx.get(idx_key, None)

        if not entry:
            raise NoteNotFound()

        # TODO: Handle possible JSON errors
        note = Note(**entry)
        note_path = self._get_note_content_path(note.id)

        # Remove note content
        Path(note_path).unlink()
        # Update the index
        self.idx.pop(idx_key)

    @staticmethod
    def _get_index_key(filepath: str, line: int) -> str:
        return f"{filepath}:{line}"

    def _get_note_content_path(self, note_id: str) -> str:
        notes_folder = Path(self.notter.get_config(ncons.NOTES_PATH))
        return str(notes_folder / note_id)
