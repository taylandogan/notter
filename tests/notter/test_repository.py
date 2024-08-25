from pathlib import Path
from unittest.mock import MagicMock, call, patch
import notter.constants as ncons
from notter.model import Comment, Content, Note, NoteType, NoteWithContent
from notter.notter import Notter
from notter.repository import SQLiteRepository


class TestSQLiteRepository:
    mock_src_folder = Path("mock/notter/src")

    @patch("notter.repository.DatabaseManager")
    def test_initialize(self, mock_db_manager: MagicMock, notter_with_config: Notter) -> None:
        assert notter_with_config.get_config(ncons.DB_INITIALIZED_FLAG) is False
        repository = SQLiteRepository(notter_with_config)
        repository.db_manager = mock_db_manager
        assert notter_with_config.get_config(ncons.DB_INITIALIZED_FLAG) is True

    @patch("notter.repository.DatabaseManager")
    def test_create(self, mock_db_manager: MagicMock, note_with_content: NoteWithContent) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        repository.create(note_with_content)

        repository.db_manager.insert.assert_called_once_with(note_with_content)

    @patch("notter.repository.DatabaseManager")
    def test_read(self, mock_db_manager: MagicMock, note_with_content: NoteWithContent) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        mock_db_manager.get_by_filepath_and_line.return_value = note_with_content
        repository.db_manager = mock_db_manager

        return_val = repository.read("dummy_path", 5)

        repository.db_manager.get_by_filepath_and_line.assert_called_once_with("dummy_path", 5)
        assert return_val == note_with_content

    @patch("notter.repository.DatabaseManager")
    def test_read_file(self, mock_db_manager: MagicMock, note_with_content: NoteWithContent) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        mock_db_manager.get_by_filepath.return_value = [note_with_content]
        repository.db_manager = mock_db_manager

        return_val = repository.read_file("dummy_path")

        repository.db_manager.get_by_filepath.assert_called_once_with("dummy_path")
        assert return_val == [note_with_content]

    @patch("notter.repository.DatabaseManager")
    def test_read_user_notes(self, mock_db_manager: MagicMock, note_with_content: NoteWithContent) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        mock_db_manager.get_by_username.return_value = [note_with_content]
        repository.db_manager = mock_db_manager

        return_val = repository.read_user_notes("pikachu")

        repository.db_manager.get_by_username.assert_called_once_with("pikachu")
        assert return_val == [note_with_content]

    @patch("notter.repository.DatabaseManager")
    def test_search(self, mock_db_manager: MagicMock, note_with_content: NoteWithContent) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        mock_db_manager.search.return_value = [note_with_content]
        repository.db_manager = mock_db_manager

        return_val = repository.search("dummy_query")

        repository.db_manager.search.assert_called_once_with("dummy_query")
        assert return_val == [note_with_content]

    @patch("notter.repository.DatabaseManager")
    def test_update(self, mock_db_manager: MagicMock, note_with_content: NoteWithContent) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        repository.db_manager = mock_db_manager

        repository.update("dummy_path", 5, note_with_content)

        repository.db_manager.update.assert_called_once_with("dummy_path", 5, note_with_content)

    @patch("notter.repository.DatabaseManager")
    def test_delete(self, mock_db_manager: MagicMock) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        repository.db_manager = mock_db_manager

        repository.delete("dummy_path", 5)

        repository.db_manager.delete.assert_called_once_with("dummy_path", 5)

    @patch("notter.repository.SQLiteRepository.delete")
    @patch("notter.repository.DatabaseManager")
    def test_prune(
        self, mock_db_manager: MagicMock, mock_delete: MagicMock
    ) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        repository.db_manager = mock_db_manager

        mock_delete.return_value = None

        repository.db_manager.get_all.return_value = [
            NoteWithContent(
                note=Note(id="1", username="pikachu", email="dummy", filepath="file1.py", line=1),
                content=Content(text="Note 1"),
            ),
            NoteWithContent(
                note=Note(id="1", username="pikachu", email="dummy", filepath="file1.py", line=2),
                content=Content(text="Note 2"),
            ),
            NoteWithContent(
                note=Note(id="1", username="pikachu", email="dummy", filepath="file2.py", line=1),
                content=Content(text="Note 3"),
            ),
            NoteWithContent(
                note=Note(id="1", username="pikachu", email="dummy", filepath="file2.py", line=2),
                content=Content(text="Note 4"),
            ),
        ]

        comments = [
            Comment("file1.py", "content1", 1, NoteType.TODO),
            Comment("file1.py", "content2", 2, NoteType.TODO),
            Comment("file3.py", "content3", 1, NoteType.TODO),
        ]
        items_to_prune = repository.prune(comments, None)

        expected_calls = [call("file2.py", 1), call("file2.py", 2)]
        mock_delete.assert_has_calls(expected_calls, any_order=True)
        assert sorted(items_to_prune) == ["file2.py:1", "file2.py:2"]
