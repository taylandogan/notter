from pathlib import Path
from typing import List

import notter.constants as ncons
from notter.db_manager import DatabaseManager
from notter.model import Comment, NoteWithContent
from notter.notter import Notter
from notter.utils import convert_to_local_path


class BaseRepository:
    def __init__(self, notter: Notter) -> None:
        raise NotImplementedError

    def create(self, note_with_content: NoteWithContent) -> None:
        raise NotImplementedError

    def read(self, filepath: str, line: int) -> NoteWithContent:
        raise NotImplementedError

    def update(self, filepath: str, line: int, note_with_content: NoteWithContent) -> None:
        raise NotImplementedError

    def delete(self, filepath: str, line: int) -> None:
        raise NotImplementedError


class SQLiteRepository(BaseRepository):
    def __init__(self, notter: Notter) -> None:
        self.notter = notter

        db_initialized = self.notter.get_config(ncons.DB_INITIALIZED_FLAG)
        notter_path = Path(self.notter.get_config(ncons.PATH))
        notes_db_path = str(notter_path / ncons.NOTES_DB_FILENAME)

        self.db_manager = DatabaseManager(notes_db_path)
        if not db_initialized:
            self.db_manager.create_tables()
            self.notter.set_config(ncons.DB_INITIALIZED_FLAG, True)

    def create(self, note_with_content: NoteWithContent) -> None:
        self.db_manager.insert(note_with_content)

    def read(self, filepath: str, line: int) -> NoteWithContent:
        return self.db_manager.get_by_filepath_and_line(filepath, line)

    def read_file(self, filepath: str) -> List[NoteWithContent]:
        return self.db_manager.get_by_filepath(filepath)

    def read_user_notes(self, username: str) -> List[NoteWithContent]:
        return self.db_manager.get_by_username(username)

    def search(self, content: str) -> List[NoteWithContent]:
        return self.db_manager.search(content)

    def update(self, filepath: str, line: int, note_with_content: NoteWithContent) -> None:
        self.db_manager.update(filepath, line, note_with_content)

    def delete(self, filepath: str, line: int) -> None:
        self.db_manager.delete(filepath, line)

    def prune(self, comments: List[Comment]) -> List[str]:
        comments_set = set()
        for comment in comments:
            filepath = convert_to_local_path(comment.filepath, self.notter.get_config(ncons.SRC_PATH))
            comments_set.add(f"{filepath}:{comment.line}")

        entry_set = set()
        entries: List[NoteWithContent] = self.db_manager.get_all()
        for entry in entries:
            entry_set.add(f"{entry.note.filepath}:{entry.note.line}")

        items_to_prune = list(entry_set.difference(comments_set))
        for item in items_to_prune:
            filepath, line = item.split(":")
            self.delete(filepath, int(line))

        return items_to_prune
