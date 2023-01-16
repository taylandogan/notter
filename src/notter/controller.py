from notter.note import Content, Note, NoteType, NoteWithContent
from notter.notter import Notter
import notter.constants as ncons
from notter.repository import JsonFileRepository


class NoteController:
    def __init__(self, notter: Notter):
        self.notter = notter
        self.repository = JsonFileRepository(self.notter)

    def create(self, filepath: str, line: int, text: str, type: NoteType = NoteType.NOTE) -> None:
        username = self.notter.get_config(ncons.USERNAME)
        email = self.notter.get_config(ncons.EMAIL)
        # TODO: Add input validation, max number of characters for each field
        note = Note(username, email, filepath, line, type)
        content = Content(text)
        note_with_content = NoteWithContent(note, content)
        self.repository.create(note_with_content)

    def get(self) -> None:
        pass

    def update(self) -> None:
        pass

    def delete(self, filepath: str, line: int) -> None:
        self.repository.delete(filepath, line)
