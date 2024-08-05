from pathlib import Path
from unittest.mock import ANY, MagicMock, call, mock_open, patch

import pytest
from notter.notter import Notter


class TestNotter:
    mock_src_folder = Path("mock/notter/src")

    def test_notter(self) -> None:
        notter = Notter()

        assert notter.config.get("initialized") is False

    def test_notter_init(self) -> None:
        notter = Notter()
        notter.init_notter_folders = MagicMock()

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            notter.configure(self.mock_src_folder)

        assert notter.config.get("config_path") == "mock/notter/.notter/config.json"
        assert notter.config.get("src_path") == "mock/notter/src"
        assert notter.config.get("path") == "mock/notter/.notter"
        notter.init_notter_folders.assert_called_once()
        m_open.assert_called_with("mock/notter/.notter/config.json", "w+")

    def test_notter_init_folders(self) -> None:
        notter = Notter()
        notter.set_config = MagicMock()
        notter.config = {"path": "mock/notter/.notter"}

        with patch("os.mkdir") as mkdir_mock:
            notter.init_notter_folders()
            mkdir_mock.call_count == 2

        notter.set_config.assert_called_once_with("initialized", True)

    def test_notter_init_already_initialized(self) -> None:
        notter = Notter()
        notter.set_config = MagicMock()
        notter.config = {"initialized": True, "path": "dummy_path"}

        with patch("os.mkdir") as mkdir_mock:
            notter.init_notter_folders()
            mkdir_mock.assert_not_called()

        notter.set_config.assert_not_called()

    @patch("notter.notter.load_config")
    def test_load(self, load_config_mock: MagicMock) -> None:
        notter = Notter()
        notter.config = {"path": "mock/notter/.notter"}
        load_config_mock.return_value = True

        notter.load(self.mock_src_folder)

        load_config_mock.assert_called_once()

    @patch("notter.notter.load_config")
    def test_load_not_initialized(self, load_config_mock: MagicMock) -> None:
        notter = Notter()
        notter.config = {"path": "mock/notter/.notter"}
        load_config_mock.return_value = False

        with pytest.raises(SystemExit):
            notter.load(self.mock_src_folder)

        load_config_mock.assert_called_once()

    @patch("notter.notter.rmtree")
    def test_destroy(self, rmtree_mock: MagicMock) -> None:
        notter = Notter()
        notter.config = {"path": "mock/notter/.notter", "initialized": True}

        notter.destroy()
        rmtree_mock.assert_called_once_with("mock/notter/.notter")

    def test_repr_config(self) -> None:
        notter = Notter()
        notter.config = {"path": "mock/notter/.notter", "initialized": True}

        assert notter.repr_config() == "Notter config:\n==============\npath: mock/notter/.notter\ninitialized: True"

    def test_get_config(self) -> None:
        notter = Notter()
        notter.config = {"path": "mock/notter/.notter", "initialized": True}

        assert notter.get_config("path") == "mock/notter/.notter"
        assert notter.get_config("initialized") is True

    def test_get_config_not_found(self) -> None:
        notter = Notter()
        notter.config = {"path": "mock/notter/.notter", "initialized": True}

        result = notter.get_config("not_found")
        assert result is None

    @patch("notter.notter.persist_config_after")
    def test_set_config(self, persist_config_mock: MagicMock) -> None:
        notter = Notter()
        notter.config = {"config_path": "mock/notter/.notter/config.json"}

        m_open = mock_open()
        with patch("builtins.open", m_open) as mock_file:
            notter.set_config("path", "new_path")

        m_open.assert_called_with("mock/notter/.notter/config.json", "w+")
        assert notter.config.get("path") == "new_path"
