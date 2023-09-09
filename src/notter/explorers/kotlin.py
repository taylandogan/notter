from notter.constants import KOTLIN_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(KOTLIN_EXT)
class KotlinExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*"]
    multi_line_comment_patterns = [r"/\*.*?\*/"]
