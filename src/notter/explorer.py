import glob
import io
import tokenize
from pathlib import Path
from typing import List

import notter.constants as ncons
from notter.model import Comment, NoteType
from notter.notter import Notter


class BaseExplorer:
    def __init__(self, notter: Notter):
        raise NotImplementedError

    def discover(self, tags: List[str]) -> List[Comment]:
        raise NotImplementedError


class LexicalExplorer(BaseExplorer):
    def __init__(self, notter: Notter) -> None:
        self.source_path = notter.get_config(ncons.SRC_PATH)

    def discover(self, tags: List[str]) -> List[Comment]:
        comments = []
        tags = [tag.lower() for tag in tags]
        glob_pattern = str(Path(self.source_path) / "**/*.py")

        for file in glob.glob(glob_pattern, recursive=True):
            comments_in_file = LexicalExplorer._discover_comments_in_file(file, tags)
            comments.extend(comments_in_file)

        return comments

    @staticmethod
    def _discover_comments_in_file(filepath: str, tags: List[str]) -> List[Comment]:
        comments: List[Comment] = []

        with open(filepath, "r", encoding="utf-8") as file:
            file_content = file.read()

        tokens = tokenize.tokenize(io.BytesIO(file_content.encode()).readline)
        for token_type, token_content, token_start, _, _ in tokens:
            if token_type == tokenize.COMMENT:
                token_content = token_content[1:]

                is_todo = False
                for tag in tags:
                    if tag in token_content.lower():
                        is_todo = True

                if comments and token_start[0] == (comments[-1].line + 1) and not is_todo:
                    comments[-1].text += f"\n{token_content}"
                    comments[-1].multiline = True
                else:
                    note_type = NoteType.TODO if is_todo else NoteType.NOTE
                    comments.append(Comment(filepath, token_content, token_start[0], note_type))

        return comments
