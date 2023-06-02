from pathlib import Path
from typing import List
from unittest.mock import MagicMock, call, patch, mock_open
import notter.constants as ncons
from notter.index import NoteIndex
from notter.model import Comment, Content, Note, NoteType, NoteWithContent
from notter.notter import Notter
from notter.repository import JsonFileRepository, SQLiteRepository


class TestJsonFileRepository:
    @patch("notter.index.NoteIndex.init_index")
    def test_initialize(self, init_idx_mock: MagicMock, notter_with_config: Notter) -> None:
        assert notter_with_config.config.get(ncons.NOTES_INDEX_PATH) is None
        assert notter_with_config.config.get(ncons.IDX_INITIALIZED_FLAG) is False

        repository = JsonFileRepository(notter_with_config)

        assert hasattr(repository, "note_index")
        assert isinstance(repository.note_index, NoteIndex)
        assert notter_with_config.config.get(ncons.NOTES_INDEX_PATH) is not None
        assert notter_with_config.config.get(ncons.IDX_INITIALIZED_FLAG) is True
        init_idx_mock.assert_called_once()

    @patch("notter.index.NoteIndex.load_index")
    def test_load(self, load_idx_mock: MagicMock, notter_with_config: Notter) -> None:
        notter_with_config.set_config(ncons.NOTES_INDEX_PATH, "some/path")
        notter_with_config.set_config(ncons.IDX_INITIALIZED_FLAG, True)

        repository = JsonFileRepository(notter_with_config)

        assert hasattr(repository, "note_index")
        assert isinstance(repository.note_index, NoteIndex)
        load_idx_mock.assert_called_once()

    @patch("notter.index.NoteIndex.store")
    @patch("notter.repository.JsonFileRepository._get_note_content_path")
    def test_create(
        self,
        get_content_path_mock: MagicMock,
        store_mock: MagicMock,
        notter_with_config: Notter,
        note_with_content: NoteWithContent,
    ) -> None:
        get_content_path_mock.return_value = "mock/path"
        notter_with_config.set_config(ncons.NOTES_INDEX_PATH, "some/path")
        notter_with_config.set_config(ncons.IDX_INITIALIZED_FLAG, False)
        repository = JsonFileRepository(notter_with_config)

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            repository.create(note_with_content)

        repository.note_index.store.assert_called_once_with(note_with_content.note)
        m_open.assert_called_with("mock/path", "w")

    @patch("notter.index.NoteIndex.fetch")
    @patch("notter.repository.JsonFileRepository._get_note_content_path")
    def test_read(self, get_content_path_mock: MagicMock, fetch_mock: MagicMock, notter_with_config: Notter) -> None:
        fetch_mock.return_value = Note(id="dummy_id", username="user", email="a@b.com", filepath="dummy_path", line=5)
        get_content_path_mock.return_value = "mock/path"
        notter_with_config.set_config(ncons.NOTES_INDEX_PATH, "some/path")
        notter_with_config.set_config(ncons.IDX_INITIALIZED_FLAG, False)
        repository = JsonFileRepository(notter_with_config)

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            fetched_note: NoteWithContent = repository.read("dummy_path", 5)

        assert fetched_note.note.id == "dummy_id"
        m_open.assert_called_with("mock/path", "r")

    @patch("notter.index.NoteIndex.store")
    @patch("notter.repository.JsonFileRepository.read")
    @patch("notter.repository.JsonFileRepository._get_note_content_path")
    def test_update(
        self, get_content_path_mock: MagicMock, read_mock: MagicMock, store_mock: MagicMock, notter_with_config: Notter
    ) -> None:
        dummy_note = Note(id="dummy_id", username="user", email="a@b.com", filepath="dummy_path", line=5)
        new_note = Note(id="dummy_id", username="pikachu", email="pika@chu.com", filepath="dummy_path", line=5)

        existing_note = NoteWithContent(dummy_note, Content("old content"))
        read_mock.return_value = existing_note
        get_content_path_mock.return_value = "mock/path"
        notter_with_config.set_config(ncons.NOTES_INDEX_PATH, "some/path")
        notter_with_config.set_config(ncons.IDX_INITIALIZED_FLAG, False)
        repository = JsonFileRepository(notter_with_config)

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            repository.update("dummy_path", 5, NoteWithContent(new_note, Content("new content")))

        m_open.assert_called_with("mock/path", "w")
        read_mock.assert_called_once_with("dummy_path", 5)
        store_mock.assert_called_once_with(existing_note.note, True)

    @patch("notter.index.NoteIndex.clean")
    @patch("notter.repository.JsonFileRepository._get_note_content_path")
    def test_delete(self, get_content_path_mock: MagicMock, clean_mock: MagicMock, notter_with_config: Notter) -> None:
        get_content_path_mock.return_value = "mock/path"
        clean_mock.return_value = Note(id="dummy_id", username="user", email="a@b.com", filepath="dummy_path", line=5)
        notter_with_config.set_config(ncons.NOTES_INDEX_PATH, "some/path")
        notter_with_config.set_config(ncons.IDX_INITIALIZED_FLAG, False)
        repository = JsonFileRepository(notter_with_config)

        with patch("os.unlink") as mock_unlink:
            repository.delete("dummy_path", 5)

        clean_mock.assert_called_once_with("dummy_path", "5")
        get_content_path_mock.assert_called_once_with("dummy_id")

    @patch("notter.index.NoteIndex.summarize")
    @patch("notter.repository.JsonFileRepository.delete")
    def test_prune(self, delete_mock: MagicMock, summarize_mock: MagicMock, notter_with_config: Notter) -> None:
        summarize_mock.return_value = set(["mock_path1:2", "mock_path2:3", "mock_path2:4"])
        notter_with_config.set_config(ncons.NOTES_INDEX_PATH, "some/path")
        notter_with_config.set_config(ncons.IDX_INITIALIZED_FLAG, False)
        repository = JsonFileRepository(notter_with_config)
        comments: List[Comment] = [
            Comment("mock_path1", "text", 2, NoteType.TODO),
            Comment("mock_path2", "texttext", 4, NoteType.NOTE),
        ]

        items_to_prune = repository.prune(comments)

        assert items_to_prune == ["mock_path2:3"]
        delete_mock.assert_called_once_with("mock_path2", 3)
        summarize_mock.assert_called_once_with()

    def test_get_note_content_path(self, notter_with_config: Notter) -> None:
        notter_with_config.set_config(ncons.NOTES_PATH, "note/path")
        notter_with_config.set_config(ncons.IDX_INITIALIZED_FLAG, False)
        repository = JsonFileRepository(notter_with_config)

        assert repository._get_note_content_path("dummy_id") == "note/path/dummy_id"


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

    @patch("notter.utils.convert_to_local_path")
    @patch("notter.repository.SQLiteRepository.delete")
    @patch("notter.repository.DatabaseManager")
    def test_prune(
        self, mock_db_manager: MagicMock, mock_delete: MagicMock, mock_convert_to_local_path: MagicMock
    ) -> None:
        notter_with_config = Notter()
        notter_with_config.configure(self.mock_src_folder)
        repository = SQLiteRepository(notter_with_config)
        repository.db_manager = mock_db_manager

        mock_delete.return_value = None
        mock_convert_to_local_path = MagicMock(side_effect=lambda x: x)

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
        items_to_prune = repository.prune(comments)

        expected_calls = [call("file2.py", 1), call("file2.py", 2)]
        mock_delete.assert_has_calls(expected_calls, any_order=True)
        assert sorted(items_to_prune) == ["file2.py:1", "file2.py:2"]
