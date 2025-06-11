from functools import cache
from typing import Any

from caseconverter import kebabcase
from .renderers import default_markdown_parser



@cache
def _type_css(vm: Any) -> str:
    """ Returns the default CSS class for the given view model. """
    return " ".join(
        kebabcase(t.__qualname__)
        for t in type(vm).mro()
        if t != object
    )

j2_functions: dict[str, Any] = dict(
    markdown = default_markdown_parser.render,
    type_css = _type_css,
)
