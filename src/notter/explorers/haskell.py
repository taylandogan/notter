from notter.constants import HASKELL_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(HASKELL_EXT)
class HaskellExplorer(RegexExplorer):
    single_line_comment_patterns = [r"--.*"]
    multi_line_comment_patterns = [r"{-.*?-}"]
