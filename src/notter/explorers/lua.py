from notter.constants import LUA_EXT
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(LUA_EXT)
class LuaExplorer(RegexExplorer):
    single_line_comment_patterns = [r"--.*"]
    multi_line_comment_patterns = [r"--\[\[.*?\]\]"]
