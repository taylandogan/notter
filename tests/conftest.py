import os
from pathlib import Path
import shutil
from typing import Generator
from notter.model import Content, Note, NoteType, NoteWithContent
from pytest import fixture
from notter.controller import NoteController

from notter.notter import Notter


@fixture
def content() -> Content:
    return Content("This is a note")


@fixture
def note() -> Note:
    return Note(
        id="note_id",
        username="pikachu",
        email="pikachu@test.com",
        filepath="path/to/file",
        line=1,
        type=NoteType.TODO,
        created_at="2021-01-01T00:00:00",
        updated_at="2021-02-01T10:00:00",
    )


@fixture
def note_with_content(note: Note, content: Content) -> NoteWithContent:
    return NoteWithContent(note, content)


@fixture
def temp_directory() -> Generator[Path, None, None]:
    test_dir: Path = Path(__file__).parent.resolve()
    tmp_dir: Path = test_dir / "tmp"

    os.makedirs(str(tmp_dir), exist_ok=True)
    yield tmp_dir
    shutil.rmtree(str(tmp_dir))


@fixture
def notter_with_config(temp_directory: Path) -> Notter:
    notter = Notter()
    notter.configure(temp_directory / "src")
    return notter


@fixture
def note_controller(notter_with_config) -> NoteController:
    return NoteController(notter_with_config)
