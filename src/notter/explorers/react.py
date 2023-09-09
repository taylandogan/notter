from notter.constants import REACT_EXT, REACT_TS_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(REACT_EXT)
class ReactExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*|<!--.*?-->"]
    multi_line_comment_patterns = [r"/\*.*?\*/|<!--.*?[\r\n]+.*?-->"]


@register_explorer(REACT_TS_EXT)
class ReactTSExplorer(ReactExplorer):
    pass
