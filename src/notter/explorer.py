import glob
import io
import tokenize
from pathlib import Path
from typing import List

import notter.constants as ncons
from notter.model import Comment
from notter.notter import Notter


class BaseExplorer:
    def __init__(self, notter: Notter):
        raise NotImplementedError

    def discover(self) -> None:
        raise NotImplementedError


class LexicalExplorer(BaseExplorer):
    def __init__(self, notter: Notter) -> None:
        self.source_path = notter.get_config(ncons.SRC_PATH)

    def discover(self, tags: List[str]) -> None:
        comments = []
        glob_pattern = str(Path(self.source_path) / "**/*.py")

        for file in glob.glob(glob_pattern, recursive=True):
            comments_in_file = LexicalExplorer._discover_comments_in_file(file)
            comments.extend(comments_in_file)
            # TODO: Merge comments that are next to each other
            # TODO: Determine types of comments according to tags

        return comments

    @staticmethod
    def _discover_comments_in_file(filepath: str) -> List[Comment]:
        comments = []

        with open(filepath, "r", encoding="utf-8") as file:
            file_content = file.read()

        tokens = tokenize.tokenize(io.BytesIO(file_content.encode()).readline)
        for token_type, token_content, token_start, token_end, token_line in tokens:
            if token_type == tokenize.COMMENT:
                token_content = token_content[1:]
                comments.append(Comment(filepath, token_content, token_start[0], False))

        return comments
