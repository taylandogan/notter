from notter.constants import JAVASCRIPT_EXT, TYPESCRIPT_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(JAVASCRIPT_EXT)
class JavascriptExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*"]
    multi_line_comment_patterns = [r"/\*.*?\*/"]


@register_explorer(TYPESCRIPT_EXT)
class TypescriptExplorer(JavascriptExplorer):
    pass
