import pytest
from notter.utils import convert_to_local_path


class TestUtils:
    @pytest.mark.parametrize(
        "filepath, src_path, expected",
        [
            ("/home/user/notes.py", "/home/user/notes", ".py"),
            ("/home/user/notes.py", "/home/user", "notes.py"),
            ("/home/user/notes.py", "/home", "user/notes.py"),
            ("home/user/notes.py", "src_path_not_in", "home/user/notes.py"),
            ("/home/user/notes.py", "src_path_not_in", "home/user/notes.py"),
        ],
    )
    def test_convert_to_local_path(self, filepath: str, src_path: str, expected: str) -> None:
        assert convert_to_local_path(filepath, src_path) == expected
