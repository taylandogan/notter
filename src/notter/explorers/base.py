import asyncio
import os
from pathlib import Path
from typing import Dict, List

import aiofiles

import notter.constants as ncons
from notter.explorers.registry import registry
from notter.model import Comment, NoteType
from notter.notter import Notter


class BaseExplorer:
    def __init__(self, notter: Notter):
        raise NotImplementedError

    async def discover(self, tags: List[str]) -> List[Comment]:
        raise NotImplementedError


class LexicalExplorer(BaseExplorer):
    def __init__(self, notter: Notter) -> None:
        self.notter = notter
        self.source_path = notter.get_config(ncons.SRC_PATH)

    async def discover(self, tags: List[str]) -> List[Comment]:
        comments = []
        tags = [tag.lower() for tag in tags]

        files_per_ext = LexicalExplorer._find_files_with_extensions(
            str(Path(self.source_path)), ncons.SUPPORTED_EXTENSIONS
        )

        for ext, files in files_per_ext.items():
            explorer_class = registry.get(ext)

            # Skip if unrecognized file format
            if not explorer_class:
                continue

            explorer = explorer_class(self.notter)

            # Read and process files chunk by chunk
            read_file_calls = [LexicalExplorer._read_file_async(file) for file in files]
            results = dict(zip(files, await asyncio.gather(*read_file_calls, return_exceptions=True)))
            file_contents: Dict[str, str] = {
                file: content for file, content in results.items() if isinstance(content, str)
            }

            # Discover comments in files
            for file, content in file_contents.items():
                discovered_comments = explorer._discover_todos_in_file(file, content, tags)
                comments.extend(discovered_comments)

        return comments

    async def discover_single_file(self, tags: List[str], filepath: str) -> List[Comment]:
        tags = [tag.lower() for tag in tags]

        file_ext = os.path.splitext(filepath)[-1].lower()
        explorer_class = registry.get(file_ext)
        if not explorer_class:
            return []

        explorer = explorer_class(self.notter)
        file_content = await LexicalExplorer._read_file_async(filepath)
        return explorer._discover_todos_in_file(filepath, file_content, tags)

    @staticmethod
    async def _read_file_async(filepath: str) -> str:
        async with aiofiles.open(filepath, "r", encoding="utf-8") as file:
            file_content = await file.read()
        return file_content

    @staticmethod
    def _find_files_with_extensions(source_path: str, extensions: List[str]) -> Dict[str, List[str]]:
        found_files: Dict[str, List[str]] = {ext: [] for ext in extensions}

        for root, dirs, files in os.walk(source_path):
            for file in files:
                file_ext = os.path.splitext(file)[-1].lower()
                if file_ext in extensions:
                    found_files[file_ext].append(os.path.join(root, file))

        return found_files

    @classmethod
    def _discover_comments_in_file(cls, filepath: str, file_content: str, tags: List[str]) -> List[Comment]:
        raise NotImplementedError

    @classmethod
    def _discover_todos_in_file(cls, filepath: str, file_content: str, tags: List[str]) -> List[Comment]:
        comments: List[Comment] = cls._discover_comments_in_file(filepath, file_content, tags)
        return [comment for comment in comments if comment.type == NoteType.TODO]

    @staticmethod
    def determine_note_type(text: str, tags: List[str]) -> NoteType:
        text = text.lower().strip()
        tags = [tag.lower() for tag in tags]
        return NoteType.TODO if any(tag in text for tag in tags) else NoteType.NOTE
