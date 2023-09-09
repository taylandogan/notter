from notter.constants import PHP_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(PHP_EXT)
class PHPExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*|/\#.*"]
    multi_line_comment_patterns = [r"/\*.*?\*/"]
