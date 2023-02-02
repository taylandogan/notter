import notter.constants as ncons
from notter.note import Content, Note, NoteType, NoteWithContent
from notter.notter import Notter
from notter.repository import JsonFileRepository


class NoteController:
    def __init__(self, notter: Notter):
        self.notter = notter
        self.repository = JsonFileRepository(self.notter)

    def _create_note_with_content(self, filepath: str, line: int, text: str, type: NoteType) -> NoteWithContent:
        username = self.notter.get_config(ncons.USERNAME)
        email = self.notter.get_config(ncons.EMAIL)
        # TODO: Add input validation, max number of characters for each field
        note = Note(username, email, filepath, line, type)
        content = Content(text)
        return NoteWithContent(note, content)

    def create(self, filepath: str, line: int, text: str, type: NoteType = NoteType.NOTE) -> None:
        note_with_content = self._create_note_with_content(filepath, line, text, type)
        self.repository.create(note_with_content)

    def read(self, filepath: str, line: int) -> NoteWithContent:
        return self.repository.read(filepath, line)

    def update(self, filepath: str, line: int, text: str, type: NoteType = NoteType.NOTE) -> None:
        note_with_content = self._create_note_with_content(filepath, line, text, type)
        self.repository.update(filepath, line, note_with_content)

    def delete(self, filepath: str, line: int) -> None:
        self.repository.delete(filepath, line)
