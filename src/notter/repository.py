import json
from datetime import datetime
from pathlib import Path

import notter.constants as ncons
from notter.index import NoteIndex
from notter.model import Content, Note, NoteWithContent
from notter.notter import Notter
from notter.utils import CustomEncoder


class BaseRepository:
    def __init__(self, notter: Notter):
        raise NotImplementedError

    def create(self, note: Note):
        raise NotImplementedError

    def read(self) -> None:
        raise NotImplementedError

    def update(self) -> None:
        raise NotImplementedError

    def delete(self) -> None:
        raise NotImplementedError


class JsonFileRepository(BaseRepository):
    def __init__(self, notter: Notter) -> None:
        self.notter = notter

        idx_initialized = self.notter.get_config(ncons.IDX_INITIALIZED_FLAG)
        notter_path = Path(self.notter.get_config(ncons.PATH))
        note_idx_path = notter_path / ncons.NOTES_INDEX_FILENAME

        self.note_index: NoteIndex = NoteIndex(note_idx_path)

        if not idx_initialized:
            self.note_index.init_index(note_idx_path)
            self.notter.set_config(ncons.NOTES_INDEX_PATH, str(note_idx_path))
            self.notter.set_config(ncons.IDX_INITIALIZED_FLAG, True)
        else:
            self.note_index.load_index(note_idx_path)

    def create(self, note_with_content: NoteWithContent) -> None:
        # TODO: Make these two operations atomic
        # Update the index
        self.note_index.store(note_with_content.note)
        # Write note content to a file
        with open(self._get_note_content_path(note_with_content.note.id), "w") as note_file:
            note_file.write(note_with_content.content.text)

    def read(self, filepath: str, line: int) -> NoteWithContent:
        entry = self.note_index.fetch(filepath, str(line))
        note = Note(**entry)
        with open(self._get_note_content_path(note.id), "r") as note_file:
            text = note_file.read()

        content = Content(text)
        return NoteWithContent(note, content)

    def update(self, filepath: str, line: int, note_with_content: NoteWithContent) -> None:
        existing_note: NoteWithContent = self.read(filepath, str(line))
        existing_note.note.username = note_with_content.note.username
        existing_note.note.email = note_with_content.note.email
        existing_note.note.filepath = note_with_content.note.filepath
        existing_note.note.line = note_with_content.note.line
        existing_note.note.type = note_with_content.note.type
        existing_note.note.updated_at = datetime.now().isoformat()
        existing_note.content = note_with_content.content

        # TODO: Make these two operations atomic
        # Update the index
        self.note_index.store(existing_note.note, True)
        # Write note content to a file
        with open(self._get_note_content_path(existing_note.note.id), "w") as note_file:
            note_file.write(existing_note.content.text)

    def delete(self, filepath: str, line: int) -> None:
        # TODO: Make these two operations atomic
        # Update the index
        entry = self.note_index.clean(filepath, str(line))
        note = Note(**entry)
        note_path = self._get_note_content_path(note.id)
        # Remove note content
        Path(note_path).unlink()

    def _get_note_content_path(self, note_id: str) -> str:
        notes_folder = Path(self.notter.get_config(ncons.NOTES_PATH))
        return str(notes_folder / note_id)
