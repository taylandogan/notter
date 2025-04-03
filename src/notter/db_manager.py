import sqlite3
from datetime import datetime
from typing import Any

from notter import sql_statements
from notter.exceptions import NoteNotFound
from notter.model import NoteWithContent


# TODO: Check if this is the best way to do this
class ConnectionManager:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


# TODO: Add tests for DatabaseManager
class DatabaseManager:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.conn = ConnectionManager(db_name)

    def run_statement(self, statement: str, values: tuple | None = None, many: bool = False) -> list[Any] | Any:
        cursor, result = None, None

        with self.conn as conn:
            if values:
                cursor = conn.execute(statement, values)
            else:
                cursor = conn.execute(statement)

            conn.commit()
            result = cursor.fetchall() if many else cursor.fetchone()
        return result

    def create_tables(self) -> None:
        self.run_statement(sql_statements.CREATE_NOTE_TABLE)

    def get(self, note_id: str) -> NoteWithContent:
        cursor = self.run_statement(sql_statements.GET_NOTE, (note_id,))
        if not cursor:
            raise NoteNotFound
        return NoteWithContent.from_db_row(cursor)  # type: ignore [arg-type]

    def insert(self, note: NoteWithContent) -> None:
        self.run_statement(sql_statements.INSERT_NOTE, note.to_db_row())

    def update(self, filepath: str, line: int, update: NoteWithContent) -> None:
        existing: NoteWithContent = self.get_by_filepath_and_line(filepath, line)
        existing.note.filepath = update.note.filepath
        existing.note.line = update.note.line
        existing.note.type = update.note.type
        existing.note.updated_at = datetime.now().isoformat()
        existing.content = update.content

        update_tuple = existing.to_db_row()[1:] + (existing.note.id,)
        self.run_statement(sql_statements.UPDATE_NOTE, update_tuple)

    def delete(self, filepath: str, line: int) -> None:
        existing: NoteWithContent = self.get_by_filepath_and_line(filepath, line)
        self.run_statement(sql_statements.DELETE_NOTE, (existing.note.id,))

    def delete_all_in_file(self, filepath: str) -> None:
        self.run_statement(sql_statements.DELETE_NOTES_IN_FILE, (filepath,))

    def get_all(self) -> list[NoteWithContent]:
        cursor = self.run_statement(sql_statements.GET_NOTES, None, True)
        return [NoteWithContent.from_db_row(row) for row in cursor]

    def get_by_filepath(self, filepath: str) -> list[NoteWithContent]:
        cursor = self.run_statement(sql_statements.GET_NOTE_BY_FILEPATH, (filepath,), True)
        return [NoteWithContent.from_db_row(row) for row in cursor]

    def get_by_filepath_and_line(self, filepath: str, line: int) -> NoteWithContent:
        cursor = self.run_statement(sql_statements.GET_NOTE_BY_FILEPATH_AND_LINE, (filepath, line))
        if not cursor:
            raise NoteNotFound
        return NoteWithContent.from_db_row(cursor)  # type: ignore [arg-type]

    def get_by_type(self, type: str) -> list[NoteWithContent]:
        cursor = self.run_statement(sql_statements.GET_NOTE_BY_TYPE, (type,), True)
        return [NoteWithContent.from_db_row(row) for row in cursor]

    def search(self, content: str) -> list[NoteWithContent]:
        cursor = self.run_statement(sql_statements.SEARCH_NOTES_WITH_CONTENT, (f"%{content}%",), True)
        return [NoteWithContent.from_db_row(row) for row in cursor]
