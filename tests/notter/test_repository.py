from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch, mock_open
import notter.constants as ncons
from notter.index import NoteIndex
from notter.model import Comment, Content, Note, NoteType, NoteWithContent
from notter.notter import Notter
from notter.repository import JsonFileRepository


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
