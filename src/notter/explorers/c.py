import notter.constants as ncons
from notter.explorers.regex import RegexExplorer
from notter.explorers.registry import register_explorer


@register_explorer(ncons.C_EXT)
class CExplorer(RegexExplorer):
    single_line_comment_patterns = [r"//.*"]
    multi_line_comment_patterns = [r"/\*.*?\*/"]


@register_explorer(ncons.CPP_EXT)
class CPPExplorer(CExplorer):
    pass


@register_explorer(ncons.HEADER_EXT)
class HExplorer(CExplorer):
    pass


@register_explorer(ncons.HEADER_CPP_EXT)
class HPPExplorer(CExplorer):
    pass


@register_explorer(ncons.C_SHARP_EXT)
class CSharpExplorer(CExplorer):
    pass
