from notter.note import NoteType
from notter.notter import Notter
from notter.repository import JsonFileRepository


class NoteController:
    def __init__(self, notter: Notter):
        self.notter = notter
        self.repository = JsonFileRepository(self.notter)

    def create(self, filepath: str, line: int, text: str, type: NoteType = NoteType.NOTE) -> None:
        pass

    def get(self) -> None:
        pass

    def update(self) -> None:
        pass

    def delete(self) -> None:
        pass
