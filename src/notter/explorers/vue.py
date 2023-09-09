from notter.constants import VUE_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(VUE_EXT)
class VueExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*|<!--.*?-->"]
    multi_line_comment_patterns = [r"/\*.*?\*/|<!--.*?[\r\n]+.*?-->"]
