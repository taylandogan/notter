from notter.constants import RUST_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(RUST_EXT)
class RustExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*"]
    multi_line_comment_patterns = [r"/\*.*?\*/"]
