from pathlib import Path
from pytest import fixture
from notter.controller import NoteController

from notter.notter import Notter
from notter.repository import JsonFileRepository


@fixture
def notter_instance() -> Notter:
    return Notter()


@fixture
def notter_with_config() -> Notter:
    test_dir: Path = Path(__file__).parent.resolve()
    tmp_dir: Path = test_dir / "tmp"

    notter = Notter()
    notter.configure(tmp_dir / "src")
    return notter


@fixture
def note_controller(notter_with_config) -> NoteController:
    return NoteController(notter_with_config)

