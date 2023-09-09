from notter.constants import SWIFT_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(SWIFT_EXT)
class SwiftExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*"]
    multi_line_comment_patterns = [r"/\*.*?\*/"]
