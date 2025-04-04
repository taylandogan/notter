from collections.abc import Callable
from typing import Any

registry = {}


def register_explorer(extension: str) -> Callable[..., Any]:
    def wrapper(explorer_cls: Any) -> Any:
        registry[extension] = explorer_cls
        return explorer_cls

    return wrapper
