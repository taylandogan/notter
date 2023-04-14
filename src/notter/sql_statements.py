CREATE_NOTE_TABLE = """
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    username TEXT,
    email TEXT,
    filepath TEXT,
    line INTEGER,
    type TEXT,
    created_at TEXT,
    updated_at TEXT,
    content TEXT,
    UNIQUE(filepath, line) ON CONFLICT IGNORE
)
"""

INSERT_NOTE = """
INSERT INTO notes (
    id,
    username,
    email,
    filepath,
    line,
    type,
    created_at,
    updated_at,
    content
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

UPDATE_NOTE = """
UPDATE notes SET
    username = ?,
    email = ?,
    filepath = ?,
    line = ?,
    type = ?,
    created_at = ?,
    updated_at = ?,
    content = ? WHERE id = ?
"""

DELETE_NOTE = "DELETE FROM notes WHERE id = ?"
GET_NOTE = "SELECT * FROM notes WHERE id = ?"
GET_NOTES = "SELECT * FROM notes"
GET_NOTE_BY_FILEPATH = "SELECT * FROM notes WHERE filepath = ?"
GET_NOTE_BY_FILEPATH_AND_LINE = "SELECT * FROM notes WHERE filepath = ? AND line = ?"
GET_NOTE_BY_TYPE = "SELECT * FROM notes WHERE type = ?"
GET_NOTE_BY_USERNAME = "SELECT * FROM notes WHERE username = ?"
SEARCH_NOTES_WITH_CONTENT = "SELECT * FROM notes WHERE content LIKE ?"
