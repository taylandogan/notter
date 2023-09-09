from notter.constants import R_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(R_EXT)
class RExplorer(RegexExplorer):
    single_line_comment_patterns = [r"#.*"]
    multi_line_comment_patterns = []
