import io
import tokenize
from typing import List

from notter.constants import PYTHON_EXT
from notter.explorers.base import LexicalExplorer
from notter.explorers.registry import register_explorer
from notter.model import Comment, NoteType


@register_explorer(PYTHON_EXT)
class PythonExplorer(LexicalExplorer):
    @classmethod
    def _discover_comments_in_file(cls, filepath: str, file_content: str, tags: List[str]) -> List[Comment]:
        comments: List[Comment] = []

        tokens = tokenize.tokenize(io.BytesIO(file_content.encode()).readline)
        for token_type, token_content, token_start, _, _ in tokens:
            if token_type == tokenize.COMMENT:
                token_content = token_content[1:]

                note_type = LexicalExplorer.determine_note_type(token_content, tags)
                is_todo = True if note_type == NoteType.TODO else False

                if comments and token_start[0] == (comments[-1].line + 1) and not is_todo:
                    comments[-1].text += f"\n{token_content}"
                    comments[-1].multiline = True
                else:
                    comments.append(Comment(filepath, token_content, token_start[0], note_type))

        return comments
