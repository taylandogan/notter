import json
from pathlib import Path
from uuid import uuid4

from notter.note import Note, NoteWithContent
from notter.notter import Notter
import notter.constants as ncons


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

    def create(self, note_with_content: NoteWithContent) -> None:
        notes_folder = Path(self.notter.get_config(ncons.NOTES_PATH))
        note_path = str(notes_folder / note_with_content.note.note_id)

        # Write note content to a file
        with open(note_path, "w") as note_file:
            note_file.write(note_with_content.content.text)

        # Update the index
        self.idx[f"{note_with_content.note.filepath}:{note_with_content.note.line}"] = note_with_content.note.json()
        notter_idx_path = Path(self.notter.get_config(ncons.NOTES_INDEX_PATH))
        with open(notter_idx_path, "w") as idx_file:
            idx_file.write(json.dumps(self.idx))

    def get(self) -> None:
        pass

    def update(self) -> None:
        pass

    def delete(self) -> None:
        pass
