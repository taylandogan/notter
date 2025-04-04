# NOTE: Import explorers here so that they are registered in the registry
from notter.explorers.c import (
    CExplorer,  # noqa: F401
    CPPExplorer,  # noqa: F401
    CSharpExplorer,  # noqa: F401
    HExplorer,  # noqa: F401
    HPPExplorer,  # noqa: F401
)
from notter.explorers.go import GoExplorer  # noqa: F401
from notter.explorers.haskell import HaskellExplorer  # noqa: F401
from notter.explorers.java import JavaExplorer  # noqa: F401
from notter.explorers.javascript import (
    JavascriptExplorer,  # noqa: F401
    TypescriptExplorer,  # noqa: F401
)
from notter.explorers.kotlin import KotlinExplorer  # noqa: F401
from notter.explorers.lua import LuaExplorer  # noqa: F401
from notter.explorers.perl import PerlExplorer  # noqa: F401
from notter.explorers.php import PHPExplorer  # noqa: F401
from notter.explorers.python import PythonExplorer  # noqa: F401
from notter.explorers.r import RExplorer  # noqa: F401
from notter.explorers.react import (
    ReactExplorer,  # noqa: F401
    ReactTSExplorer,  # noqa: F401
)
from notter.explorers.ruby import RubyExplorer  # noqa: F401
from notter.explorers.rust import RustExplorer  # noqa: F401
from notter.explorers.scala import ScalaExplorer  # noqa: F401
from notter.explorers.swift import SwiftExplorer  # noqa: F401
from notter.explorers.vue import VueExplorer  # noqa: F401
