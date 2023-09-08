import re
from typing import List

from notter.explorers.base import LexicalExplorer
from notter.explorers.registry import register_explorer
from notter.model import Comment


@register_explorer(".js")
class JavascriptExplorer(LexicalExplorer):
    def _discover_comments_in_file(self, filepath: str, file_content: str, tags: List[str]) -> List[Comment]:
        comments: List[Comment] = []
        single_line_comment_pattern = r"//.*"
        multi_line_comment_pattern = r"/\*.*?\*/"

        for match in re.finditer(single_line_comment_pattern, file_content):
            line_number = file_content.count("\n", 0, match.start()) + 1
            note_type = LexicalExplorer.determine_note_type(match.group(0), tags)
            comments.append(Comment(filepath, match.group(0), line_number, note_type, multiline=False))

        for match in re.finditer(multi_line_comment_pattern, file_content, re.DOTALL):
            line_number = file_content.count("\n", 0, match.start()) + 1
            note_type = LexicalExplorer.determine_note_type(match.group(0), tags)
            comments.append(Comment(filepath, match.group(0), line_number, note_type, multiline=True))

        return comments


@register_explorer(".ts")
class TypescriptExplorer(JavascriptExplorer):
    pass
