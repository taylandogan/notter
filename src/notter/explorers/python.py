import io
import tokenize
from typing import List

from notter.explorers.base import LexicalExplorer
from notter.explorers.registry import register_explorer
from notter.model import Comment, NoteType


@register_explorer(".py")
class PythonExplorer(LexicalExplorer):
    def _discover_comments_in_file(self, filepath: str, file_content: str, tags: List[str]) -> List[Comment]:
        comments: List[Comment] = []

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
