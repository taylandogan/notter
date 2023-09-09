from notter.constants import PERL_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(PERL_EXT)
class PerlExplorer(RegexExplorer):
    single_line_comment_patterns = [r"#.*"]
    multi_line_comment_patterns = []
