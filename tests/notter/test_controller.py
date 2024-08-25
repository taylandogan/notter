from pathlib import Path

import notter.constants as ncons

from unittest.mock import MagicMock, call
from notter.controller import NoteController
from notter.exceptions import NoteAlreadyExists
from notter.model import Comment, NoteWithContent


class TestNoteController:
    def test_create_note_with_content(self, note_controller: NoteController) -> None:
        file_path = Path(note_controller.notter.get_config(ncons.SRC_PATH)) / "path/to/file.py"
        note_with_content = note_controller._create_note_with_content(str(file_path), 1, "This is a test", "NOTE")

        assert note_with_content.note.filepath == str(file_path)
        assert note_with_content.note.line == 1
        assert note_with_content.content.text == "This is a test"
        assert note_with_content.note.type == "NOTE"
        assert isinstance(note_with_content, NoteWithContent)

    def test_create(self, note_controller: NoteController) -> None:
        mock_note = "pikachu"
        note_controller.repository = MagicMock()
        note_controller._create_note_with_content = MagicMock(return_value=mock_note)
        note_controller.create("path/to/file.py", 1, "This is a test", "NOTE")

        note_controller.repository.create.assert_called_once_with(mock_note)

    def test_read(self, note_controller: NoteController) -> None:
        note_controller.repository = MagicMock()
        note_controller.read("path/to/file.py", 1)

        note_controller.repository.read.assert_called_once_with("path/to/file.py", 1)

    def test_read_file(self, note_controller: NoteController) -> None:
        note_controller.repository = MagicMock()
        note_controller.read_file("path/to/file.py")

        note_controller.repository.read_file.assert_called_once_with("path/to/file.py")

    def test_read_user_notes(self, note_controller: NoteController) -> None:
        note_controller.repository = MagicMock()
        note_controller.read_user_notes("pikachu")

        note_controller.repository.read_user_notes.assert_called_once_with("pikachu")

    def test_search_note_with_content(self, note_controller: NoteController) -> None:
        note_controller.repository = MagicMock()
        note_controller.search_note_with_content("test")

        note_controller.repository.search.assert_called_once_with("test")

    def test_update(self, note_controller: NoteController) -> None:
        mock_note = "pikachu"
        note_controller.repository = MagicMock()
        note_controller._create_note_with_content = MagicMock(return_value=mock_note)
        note_controller.update("path/to/file.py", 1, "This is a test", "NOTE")

        note_controller.repository.update.assert_called_once_with("path/to/file.py", 1, mock_note)

    def test_delete(self, note_controller: NoteController) -> None:
        note_controller.repository = MagicMock()
        note_controller.delete("path/to/file.py", 1)

        note_controller.repository.delete.assert_called_once_with("path/to/file.py", 1)

    async def test_discover(self, note_controller: NoteController) -> None:
        mock_comments = [
            Comment("path/to/file.py", "This is a note", 1, "NOTE"),
            Comment("path/to/file.py", "This is a todo", 2, "TODO"),
        ]

        note_controller.create = MagicMock()
        note_controller.repository = MagicMock()
        note_controller.explorer = MagicMock(discover=MagicMock(return_value=mock_comments))

        comments = await note_controller.discover(["tag1", "tag2"])

        assert comments == mock_comments
        note_controller.repository.prune.assert_called_once_with(mock_comments)
        note_controller.create.assert_has_calls(
            [call("path/to/file.py", 1, "This is a note", "NOTE"), call("path/to/file.py", 2, "This is a todo", "TODO")]
        )

    async def test_discover_no_save(self, note_controller: NoteController) -> None:
        mock_comments = [
            Comment("path/to/file.py", "This is a note", 1, "NOTE"),
            Comment("path/to/file.py", "This is a todo", 2, "TODO"),
        ]

        note_controller.create = MagicMock()
        note_controller.repository = MagicMock()
        note_controller.explorer = MagicMock(discover=MagicMock(return_value=mock_comments))

        comments = await note_controller.discover(["tag1", "tag2"], save_as_notter_notes=False)

        assert comments == mock_comments
        note_controller.repository.prune.assert_called_once_with(mock_comments)
        note_controller.create.assert_not_called()

    async def test_discover_duplicate_comment(self, note_controller: NoteController) -> None:
        mock_comments = [Comment("path/to/file.py", "This is a note", 1, "NOTE")]
        note_controller.create = MagicMock()
        note_controller.create.side_effect = NoteAlreadyExists
        note_controller.repository = MagicMock()
        note_controller.explorer = MagicMock(discover=MagicMock(return_value=mock_comments))

        comments = await note_controller.discover(["tag1", "tag2"])

        assert comments == mock_comments
        note_controller.repository.prune.assert_called_once_with(mock_comments)
        note_controller.create.assert_called_once_with("path/to/file.py", 1, "This is a note", "NOTE")

    async def test_discover_no_comments(self, note_controller: NoteController) -> None:
        mock_comments = []
        note_controller.create = MagicMock()
        note_controller.repository = MagicMock()
        note_controller.explorer = MagicMock(discover=MagicMock(return_value=mock_comments))

        comments = await note_controller.discover(["tag1", "tag2"])

        assert comments == mock_comments
        note_controller.repository.prune.assert_called_once_with(mock_comments)
        note_controller.create.assert_not_called()

    async def test_discover_no_tags(self, note_controller: NoteController) -> None:
        mock_comments = []
        note_controller.create = MagicMock()
        note_controller.repository = MagicMock()
        note_controller.explorer = MagicMock(discover=MagicMock(return_value=mock_comments))

        comments = await note_controller.discover([])

        assert comments == mock_comments
        note_controller.repository.prune.assert_called_once_with(mock_comments)
        note_controller.create.assert_not_called()
