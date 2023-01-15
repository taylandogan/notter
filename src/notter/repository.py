import json
from pathlib import Path

from notter.note import Note
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
    def __init__(self, notter: Notter):
        self.notter = notter
        self.idx = {}
        self.initialize_index_files()

    def initialize_index_files(self):
        idx_initialized = self.notter.get_config(ncons.IDX_INITIALIZED_FLAG)
        notter_path = Path(self.notter.get_config(ncons.PATH))
        note_idx_path = notter_path / ncons.NOTES_INDEX_FILENAME

        if not idx_initialized:
            with open(note_idx_path, "w+") as file:
                json.dump(self.idx, file)
            self.notter.set_config(ncons.IDX_INITIALIZED_FLAG, True)
        else:
            with open(note_idx_path, "r") as file:
                self.idx = json.loads(file.read())

    def create(self, note: Note):
        pass

    def get(self) -> None:
        pass

    def update(self) -> None:
        pass

    def delete(self) -> None:
        pass
