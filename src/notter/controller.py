import json
import uuid
from pathlib import Path

import notter.constants as ncons
from notter.exceptions import NoteAlreadyExists
from notter.explorers.base import LexicalExplorer
from notter.model import Comment, Content, Note, NoteType, NoteWithContent
from notter.notter import Notter
from notter.repository import SQLiteRepository


class NoteController:
    def __init__(self, notter: Notter):
        self.notter = notter
        self.repository = SQLiteRepository(self.notter)
        self.explorer = LexicalExplorer(self.notter)

        notter_path = Path(self.notter.get_config(ncons.PATH))
        self.export_path = str(notter_path / ncons.EXPORT_FILENAME)

    def _create_note_with_content(self, filepath: str, line: int, text: str, type: NoteType) -> NoteWithContent:
        # TODO: Add input validation, max number of characters for each field
        note = Note(str(uuid.uuid4()), filepath, line, type)
        content = Content(text)
        return NoteWithContent(note, content)

    def create(self, filepath: str, line: int, text: str, type: NoteType = NoteType.NOTE) -> None:
        note_with_content = self._create_note_with_content(filepath, line, text, type)
        self.repository.create(note_with_content)

    def get_all(self) -> list[NoteWithContent]:
        return self.repository.get_all()

    def export(self) -> None:
        todos = self.get_all()
        todo_dicts = [todo.to_dict() for todo in todos]
        with open(self.export_path, "w") as export_file:
            json.dump(todo_dicts, export_file)

    def read(self, filepath: str, line: int) -> NoteWithContent:
        return self.repository.read(filepath, line)

    def read_file(self, filepath: str) -> list[NoteWithContent]:
        return self.repository.read_file(filepath)

    def search_note_with_content(self, content: str) -> list[NoteWithContent]:
        return self.repository.search(content)

    def update(self, filepath: str, line: int, text: str, type: NoteType = NoteType.NOTE) -> None:
        note_with_content = self._create_note_with_content(filepath, line, text, type)
        self.repository.update(filepath, line, note_with_content)

    def delete(self, filepath: str, line: int) -> None:
        self.repository.delete(filepath, line)

    def delete_all_in_file(self, filepath: str) -> None:
        self.repository.delete_all_in_file(filepath)

    async def discover(self, tags: list[str], filepath: str | None = None) -> list[Comment]:
        existing_comments: list[NoteWithContent] = self.get_all()
        existing_comments_locations: list[str] = [comment.location_id for comment in existing_comments]

        comments: list[Comment] = await self.explorer.discover(tags)
        for comment in comments:
            try:
                if comment.location_id in existing_comments_locations:
                    self.update(comment.filepath, comment.line, comment.text, comment.type)
                else:
                    self.create(comment.filepath, comment.line, comment.text, comment.type)
            except NoteAlreadyExists:
                continue

        _ = self.repository.prune(comments, filepath)
        return comments

    async def discover_single_file(self, filepath: str, tags: list[str]) -> list[Comment]:
        existing_comments: list[NoteWithContent] = self.read_file(filepath)
        existing_comments_locations: list[str] = [comment.location_id for comment in existing_comments]

        try:
            comments: list[Comment] = await self.explorer.discover_single_file(tags, filepath)
        except FileNotFoundError:
            self.delete_all_in_file(filepath)
            return []

        for comment in comments:
            try:
                if comment.location_id in existing_comments_locations:
                    self.update(comment.filepath, comment.line, comment.text, comment.type)
                else:
                    self.create(comment.filepath, comment.line, comment.text, comment.type)
            except NoteAlreadyExists:
                continue

        _ = self.repository.prune(comments, filepath)
        return comments
