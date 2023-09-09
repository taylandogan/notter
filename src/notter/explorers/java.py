from notter.constants import JAVA_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(JAVA_EXT)
class JavaExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*"]
    multi_line_comment_patterns = [r"/\*.*?\*/"]
