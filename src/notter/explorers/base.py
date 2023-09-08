import os
from pathlib import Path
from typing import Dict, List

import notter.constants as ncons
from notter.model import Comment
from notter.notter import Notter
from notter.explorers.registry import registry


class BaseExplorer:
    def __init__(self, notter: Notter):
        raise NotImplementedError

    def discover(self, tags: List[str]) -> List[Comment]:
        raise NotImplementedError


class LexicalExplorer(BaseExplorer):
    def __init__(self, notter: Notter) -> None:
        self.notter = notter
        self.source_path = notter.get_config(ncons.SRC_PATH)

    def discover(self, tags: List[str]) -> List[Comment]:
        comments = []
        tags = [tag.lower() for tag in tags]

        files_per_ext = LexicalExplorer._find_files_with_extensions(
            str(Path(self.source_path)), ncons.SUPPORTED_EXTENSIONS
        )

        for ext, files in files_per_ext.items():
            explorer_class = registry.get(ext)
            if explorer_class:
                explorer = explorer_class(self.notter)
                for file in files:
                    comments.extend(explorer._discover_comments_in_file(file, tags))

        return comments

    @staticmethod
    def _find_files_with_extensions(source_path: str, extensions: List[str]) -> Dict[str, List[str]]:
        found_files: Dict[str, List[str]] = {ext: [] for ext in extensions}

        for root, dirs, files in os.walk(source_path):
            for file in files:
                file_ext = os.path.splitext(file)[-1].lower()
                if file_ext in extensions:
                    found_files[file_ext].append(os.path.join(root, file))

        return found_files

    def _discover_comments_in_file(self, filepath: str, tags: List[str]) -> List[Comment]:
        raise NotImplementedError
