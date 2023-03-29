import os
from pathlib import Path
import shutil
from typing import Generator
from pytest import fixture
from notter.controller import NoteController

from notter.notter import Notter
from notter.repository import JsonFileRepository


@fixture
def temp_directory() -> Generator[str, None, None]:
    test_dir: Path = Path(__file__).parent.resolve()
    tmp_dir: Path = test_dir / "tmp"

    os.makedirs(str(tmp_dir))
    yield tmp_dir
    shutil.rmtree(str(tmp_dir))


@fixture
def notter_instance() -> Notter:
    return Notter()


@fixture
def notter_with_config(temp_directory: Path) -> Notter:
    notter = Notter()
    notter.configure(temp_directory / "src")
    return notter


@fixture
def note_controller(notter_with_config) -> NoteController:
    return NoteController(notter_with_config)

