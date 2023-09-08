import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
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
            if explorer_class:
                explorer = explorer_class(self.notter)

                # Read all files asynchronously
                read_file_calls = [LexicalExplorer._read_file_async(file) for file in files]
                results = dict(zip(files, await asyncio.gather(*read_file_calls, return_exceptions=True)))
                file_contents: Dict[str, str] = {
                    file: content for file, content in results.items() if isinstance(content, str)
                }

                # Discover comments in files in parallel
                with ProcessPoolExecutor(max_workers=4) as executor:
                    tasks = [(file, content, tags) for file, content in file_contents.items()]
                    discovered_comments = list(executor.map(explorer._discover_comments_in_file, *zip(*tasks)))

                # Flatten list of lists of comments
                for comment_list in discovered_comments:
                    comments.extend(comment_list)

        return comments

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

    def _discover_comments_in_file(self, filepath: str, file_content: str, tags: List[str]) -> List[Comment]:
        raise NotImplementedError

    @staticmethod
    def determine_note_type(text: str, tags: List[str]) -> NoteType:
        text = text.lower()
        tags = [tag.lower() for tag in tags]
        return NoteType.TODO if any(tag in text for tag in tags) else NoteType.NOTE
