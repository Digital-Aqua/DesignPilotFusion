import logging, os
from functools import cache
from pathlib import Path
from typing import (
    Any, Awaitable, Callable, Iterable, ParamSpec, TypeVar,
    cast
)

from caseconverter import kebabcase
import jinja2 as j2
from markdown_it import MarkdownIt
from markupsafe import Markup

from designpilot.ui.base import ViewModel
from designpilot.ui.utils import MarkdownString


_log = logging.getLogger(__name__)


_P = ParamSpec('_P')
_T = TypeVar('_T')
_TVM = TypeVar('_TVM', bound=ViewModel)

AsyncCallable = Callable[_P, Awaitable[_T]]
Renderer = Callable[[_TVM], Iterable[str]]
StrPath = str | os.PathLike[str]

_renderers: dict[type[ViewModel], Any] = {}


_renderer_cache: dict[type[ViewModel], Renderer[Any] | None] = {}
def _find_renderer(vm_type: type[_TVM]) -> Renderer[_TVM] | None:
    if vm_type in _renderer_cache:
        return _renderer_cache[vm_type]
    mro = vm_type.mro()
    actual_renderer = None
    for cls in mro:
        renderer_from_dict = _renderers.get(cls, None)
        if renderer_from_dict:
            actual_renderer = _renderer_cache[vm_type] = \
                cast(Renderer[_TVM], renderer_from_dict)
            break
    return actual_renderer


# class HtmlRenderContext():
#     def __init__(self, buffer: io.StringIO):
#         self._buffer = buffer
    
#     def render(self, *vms: ViewModel) -> None:
#         for vm in vms:
#             vm_type = type(vm)
#             renderer = _find_renderer(vm_type)
#             if renderer:
#                 renderer(vm, self)
#             else:
#                 _log.warning(
#                     f"No renderer found for '{vm_type.__qualname__}'. Skipping."
#                 )
    
#     def write(self, text: str) -> None:
#         self._buffer.write(text)
    
#     def writelines(self, lines: Iterable[str]) -> None:
#         self._buffer.writelines(lines)

#     # @contextmanager
#     # def write_element(self,
#     #     element_: str,
#     #     **attrs: str
#     # ) -> _ContextBlock[Self]:
#     #     self._buffer.write('<')
#     #     self._buffer.write(element_)
#     #     for attr, value in attrs.items():
#     #         self._buffer.write(f' {escape(attr)}="{escape(value)}"')
#     #     self._buffer.write('>')
#     #     yield self
#     #     self._buffer.write('</')
#     #     self._buffer.write(element_)
#     #     self._buffer.write('>')


# def render_html(vm: ViewModel) -> Iterable[str]:
#     renderer = _find_renderer(type(vm))
#     if not renderer:
#         _log.warning(
#             f"No renderer found for '{type(vm).__qualname__}'. Skipping."
#         )
#         return []
#     return renderer(vm)


# def html_renderer(
#     vm_type: type[_TVM]
# ) -> Callable[[Renderer[_TVM]], Renderer[_TVM]]:
#     def decorator(renderer: Renderer[_TVM]) -> Renderer[_TVM]:
#         _renderers[vm_type] = renderer
#         return renderer
#     return decorator


_md = (
    MarkdownIt('commonmark', dict(
        breaks = True,
        html = True
    ))
    .enable('table')
)


@cache
def _type_css(vm: Any) -> str:
    """ Returns the default CSS class for the given view model. """
    return " ".join(
        kebabcase(t.__qualname__)
        for t in type(vm).mro()
        if t != object
    )


def render(*vms: ViewModel) -> Iterable[str]:
    for vm in vms:
        renderer = _find_renderer(type(vm))
        if not renderer:
            _log.warning(
                f"No renderer found for '{type(vm).__qualname__}'. Skipping."
            )
            continue
        for item in renderer(vm):
            yield Markup(item)


def render_as(vm_type: type[_TVM], *vms: ViewModel) -> Iterable[str]:
    for vm in vms:
        if not isinstance(vm, vm_type):
            _log.warning(
                f"'{type(vm).__qualname__}' cannot be rendered as '{vm_type.__qualname__}'. Skipping."
            )
            continue
        renderer = _find_renderer(vm_type)
        if not renderer:
            _log.warning(
                f"No renderer found for '{vm_type.__qualname__}'. Skipping."
            )
            continue
        yield from renderer(vm)


def finalize_for_render(*args: Any, **__) -> Any: # type: ignore
    obj = args[0]
    if isinstance(obj, ViewModel):
        renderer = _find_renderer(type(obj))
        if renderer:
            return Markup(''.join(renderer(obj)))
    if isinstance(obj, MarkdownString):
        return Markup(_md.render(str(obj)))
    return obj


_jinja_env = j2.Environment(
    autoescape = True,
    auto_reload = True,
    loader = j2.FileSystemLoader(
        searchpath = [
            Path(__file__).parent,
        ],
        followlinks = True
    ),
    finalize = finalize_for_render # type: ignore
)

_jinja_env.globals.update(
    type_css = _type_css,
    render = render, # type: ignore
    render_as = render_as, # type: ignore
)

def register_template(
    vm_type: type[_TVM],
    filename: str
) -> Renderer[_TVM]:
    template = _jinja_env.get_template(filename)
    def renderer(vm: _TVM) -> Iterable[str]:
        return template.generate(vm = vm)
    _renderers[vm_type] = renderer
    return renderer
