import json
from pathlib import Path
from uuid import uuid4
from notter.exceptions import NoteNotFound

from notter.note import Note, NoteWithContent
from notter.notter import Notter
import notter.constants as ncons
from notter.utils import CustomEncoder, persist_index_after


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
        self.idx = {}
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
        notes_folder = Path(self.notter.get_config(ncons.NOTES_PATH))
        note_path = str(notes_folder / note_with_content.note.note_id)

        # TODO: Make these two operations atomic
        # Write note content to a file
        with open(note_path, "w") as note_file:
            note_file.write(note_with_content.content.text)

        # Update the index
        # TODO: Handle possible JSON errors
        idx_key = JsonFileRepository._get_index_key(note_with_content.note.filepath, note_with_content.note.line)
        self.idx[idx_key] = json.dumps(note_with_content.note, cls=CustomEncoder)

    def get(self) -> None:
        pass

    @persist_index_after
    def update(self) -> None:
        pass

    @persist_index_after
    def delete(self, filepath: str, line: int) -> None:
        idx_key = JsonFileRepository._get_index_key(filepath, line)
        entry = self.idx.get(idx_key, None)

        if not entry:
            raise NoteNotFound()

        # TODO: Handle possible JSON errors
        note = Note(**json.loads(entry))
        notes_folder = Path(self.notter.get_config(ncons.NOTES_PATH))
        note_path = str(notes_folder / note.note_id)

        # Remove note content
        Path(note_path).unlink()
        # Update the index
        self.idx.pop(idx_key)

    @staticmethod
    def _get_index_key(filepath: str, line: int) -> str:
        return f"{filepath}:{line}"
