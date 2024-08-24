import json
import uuid
from pathlib import Path
from typing import List

import notter.constants as ncons
from notter.exceptions import NoteAlreadyExists
from notter.explorers.base import LexicalExplorer
from notter.model import Comment, Content, Note, NoteType, NoteWithContent
from notter.notter import Notter
from notter.repository import SQLiteRepository
from notter.utils import convert_to_local_path


class NoteController:
    def __init__(self, notter: Notter):
        self.notter = notter
        self.repository = SQLiteRepository(self.notter)
        self.explorer = LexicalExplorer(self.notter)

        notter_path = Path(self.notter.get_config(ncons.PATH))
        self.export_path = str(notter_path / ncons.EXPORT_FILENAME)

    def _create_note_with_content(self, filepath: str, line: int, text: str, type: NoteType) -> NoteWithContent:
        src_folder = self.notter.get_config(ncons.SRC_PATH)
        filepath = convert_to_local_path(filepath, src_folder)
        username = self.notter.get_config(ncons.USERNAME)
        email = self.notter.get_config(ncons.EMAIL)
        # TODO: Add input validation, max number of characters for each field
        note = Note(str(uuid.uuid4()), username, email, filepath, line, type)
        content = Content(text)
        return NoteWithContent(note, content)

    def create(self, filepath: str, line: int, text: str, type: NoteType = NoteType.NOTE) -> None:
        note_with_content = self._create_note_with_content(filepath, line, text, type)
        self.repository.create(note_with_content)

    def get_all(self) -> List[NoteWithContent]:
        return self.repository.get_all()

    def export(self) -> None:
        todos = self.get_all()
        todo_dicts = [todo.to_dict() for todo in todos]
        with open(self.export_path, "w") as export_file:
            json.dump(todo_dicts, export_file)

    def read(self, filepath: str, line: int) -> NoteWithContent:
        return self.repository.read(filepath, line)

    def read_file(self, filepath: str) -> List[NoteWithContent]:
        return self.repository.read_file(filepath)

    def read_user_notes(self, username: str) -> List[NoteWithContent]:
        return self.repository.read_user_notes(username)

    def search_note_with_content(self, content: str) -> List[NoteWithContent]:
        return self.repository.search(content)

    def update(self, filepath: str, line: int, text: str, type: NoteType = NoteType.NOTE) -> None:
        note_with_content = self._create_note_with_content(filepath, line, text, type)
        self.repository.update(filepath, line, note_with_content)

    def delete(self, filepath: str, line: int) -> None:
        self.repository.delete(filepath, line)

    async def discover(self, tags: List[str], save_as_notter_notes: bool = True) -> List[Comment]:
        comments: List[Comment] = await self.explorer.discover(tags)

        if save_as_notter_notes:
            for comment in comments:
                try:
                    self.create(comment.filepath, comment.line, comment.text, comment.type)
                except NoteAlreadyExists:
                    continue

        _ = self.repository.prune(comments)
        return comments
