from dataclasses import asdict
from unittest.mock import ANY, MagicMock, mock_open, patch

import pytest
from notter.exceptions import NoteAlreadyExists, NoteNotFound
from notter.index import NoteIndex
from notter.model import Note
from notter.utils import CustomEncoder


class TestNoteIndex:
    mock_index_path = "path/mock_index.json"
    mock_filepath = "path/mock_file.txt"
    mock_line = "1"
    mock_note_idx_entry = {"filepath": mock_filepath, "line": mock_line}
    mock_note = Note(id="dummy_id", username="user", email="a@b.com", filepath=mock_filepath, line=mock_line)

    @patch("json.dump")
    def test_init_index(self, json_dump_mock: MagicMock) -> None:
        index = NoteIndex(self.mock_index_path)

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            index.init_index(self.mock_index_path)

        m_open.assert_called_with(self.mock_index_path, "w+")
        json_dump_mock.assert_called_once_with({}, ANY, cls=CustomEncoder, indent=4)

    @patch("json.loads")
    def test_load_index(self, json_loads_mock: MagicMock) -> None:
        index = NoteIndex(self.mock_index_path)

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            index.load_index(self.mock_index_path)

        m_open.assert_called_with(self.mock_index_path, "r")
        json_loads_mock.assert_called_once()

    def test_seek(self) -> None:
        index = NoteIndex(self.mock_index_path)
        index.idx = {self.mock_filepath: {self.mock_line: self.mock_note_idx_entry}}

        assert index.seek(self.mock_filepath, self.mock_line) is True

    def test_seek_nonexistent_file_entry(self) -> None:
        index = NoteIndex(self.mock_index_path)
        assert index.seek("path/mock_file.txt", "2") is False

    def test_seek_nonexistent_line_entry(self) -> None:
        index = NoteIndex(self.mock_index_path)
        index.idx = {self.mock_filepath: {self.mock_line: self.mock_note_idx_entry}}

        assert index.seek(self.mock_filepath, "2") is False

    @patch("notter.index.NoteIndex.seek")
    def test_fetch(self, seek_mock: MagicMock) -> None:
        seek_mock.return_value = True
        index = NoteIndex(self.mock_index_path)
        index.idx = {self.mock_filepath: {self.mock_line: asdict(self.mock_note)}}

        fetched_note = index.fetch(self.mock_filepath, self.mock_line)
        assert isinstance(fetched_note, Note)
        assert fetched_note.id == self.mock_note.id

    @patch("notter.index.NoteIndex.seek")
    def test_fetch_nonexistent(self, seek_mock: MagicMock) -> None:
        seek_mock.return_value = False
        index = NoteIndex(self.mock_index_path)

        with pytest.raises(NoteNotFound):
            index.fetch("path/mock_file.txt", "2")

    def test_summarize(self) -> None:
        index = NoteIndex(self.mock_index_path)
        index.idx = {self.mock_filepath: {self.mock_line: self.mock_note}}

        result = index.summarize()
        assert isinstance(result, set)
        assert len(result) == 1
        assert result.pop() == "path/mock_file.txt:1"

    def test_summarize_empty(self) -> None:
        index = NoteIndex(self.mock_index_path)
        index.idx = {}

        result = index.summarize()
        assert isinstance(result, set)
        assert len(result) == 0

    @patch("notter.index.NoteIndex.seek")
    def test_store(self, seek_mock: MagicMock) -> None:
        seek_mock.return_value = False
        index = NoteIndex(self.mock_index_path)
        index.idx = {}

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            index.store(self.mock_note)

        m_open.assert_called_with(self.mock_index_path, "w")
        assert index.idx == {self.mock_filepath: {self.mock_line: asdict(self.mock_note)}}

    @patch("notter.index.NoteIndex.seek")
    def test_store_existing(self, seek_mock: MagicMock) -> None:
        seek_mock.return_value = True
        index = NoteIndex(self.mock_index_path)

        with pytest.raises(NoteAlreadyExists):
            index.store(self.mock_note)

    @patch("notter.index.NoteIndex.fetch")
    def test_clean(self, fetch_mock: MagicMock) -> None:
        fetch_mock.return_value = self.mock_note
        index = NoteIndex(self.mock_index_path)
        index.idx = {self.mock_filepath: {self.mock_line: self.mock_note}}

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            return_val = index.clean(self.mock_filepath, self.mock_line)

        m_open.assert_called_with(self.mock_index_path, "w")
        assert index.idx == {}
        assert return_val == self.mock_note

    @patch("notter.index.NoteIndex.fetch")
    def test_clean_nonexistent(self, fetch_mock: MagicMock) -> None:
        fetch_mock.side_effect = NoteNotFound
        index = NoteIndex(self.mock_index_path)

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            return_val = index.clean("asfjhgask", self.mock_line)

        m_open.assert_called_with(self.mock_index_path, "w")
        assert return_val is None
