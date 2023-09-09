from notter.constants import RUBY_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(RUBY_EXT)
class RubyExplorer(RegexExplorer):
    single_line_comment_patterns = [r"#.*"]
    multi_line_comment_patterns = [r"=begin.*?=\end"]
