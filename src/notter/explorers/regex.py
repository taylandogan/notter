import re
from typing import List

from notter.explorers.base import LexicalExplorer
from notter.model import Comment


class RegexExplorer(LexicalExplorer):
    single_line_comment_patterns = [r"//.*"]
    multi_line_comment_patterns = [r"/\*.*?\*/"]

    @classmethod
    def _discover_comments_in_file(cls, filepath: str, file_content: str, tags: List[str]) -> List[Comment]:
        comments: List[Comment] = []

        for pattern in cls.single_line_comment_patterns:
            for match in re.finditer(pattern, file_content):
                line_number = file_content.count("\n", 0, match.start()) + 1
                note_type = LexicalExplorer.determine_note_type(match.group(0), tags)
                comments.append(Comment(filepath, match.group(0), line_number, note_type, multiline=False))

        for pattern in cls.multi_line_comment_patterns:
            for match in re.finditer(pattern, file_content, re.DOTALL):
                line_number = file_content.count("\n", 0, match.start()) + 1
                note_type = LexicalExplorer.determine_note_type(match.group(0), tags)
                is_multiline = "\n" in match.group(0)
                comments.append(Comment(filepath, match.group(0), line_number, note_type, multiline=is_multiline))

        return comments
