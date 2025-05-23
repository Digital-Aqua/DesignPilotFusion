import io, logging
from contextlib import contextmanager
from html import escape
from typing import (
    Any, Awaitable, Callable, Generator, Iterable, ParamSpec, Self,
    TypeVar, cast
)

from designpilot.ui.base import ViewModel
from designpilot.ui.elements import (
    TextVM, ButtonVM
)


_log = logging.getLogger(__name__)


_P = ParamSpec('_P')
_T = TypeVar('_T')
_TVM = TypeVar('_TVM', bound=ViewModel)

AsyncCallable = Callable[_P, Awaitable[_T]]
Renderer = Callable[[_TVM, 'HtmlRenderContext'], None]

_ContextBlock = Generator[_T, None, None]

_renderers: dict[type[ViewModel], Any] = {}


_renderer_cache: dict[type[ViewModel], Renderer[ViewModel] | None] = {}
def _find_renderer(vm_type: type[ViewModel]) -> Renderer[ViewModel] | None:
    if vm_type in _renderer_cache:
        return _renderer_cache[vm_type]
    mro = vm_type.mro()
    actual_renderer = None
    for cls in mro:
        renderer_from_dict = _renderers.get(cls, None)
        if renderer_from_dict:
            actual_renderer = _renderer_cache[vm_type] = \
                cast(Renderer[ViewModel], renderer_from_dict)
            break
    return actual_renderer


class HtmlRenderContext():
    def __init__(self, buffer: io.StringIO):
        self._buffer = buffer
    
    def render(self, *vms: ViewModel) -> None:
        for vm in vms:
            vm_type = type(vm)
            renderer = _find_renderer(vm_type)
            if renderer:
                renderer(vm, self)
            else:
                _log.warning(
                    f"No renderer found for '{vm_type.__qualname__}'. Skipping."
                )
    
    def write(self, text: str) -> None:
        self._buffer.write(text)
    
    def writelines(self, lines: Iterable[str]) -> None:
        self._buffer.writelines(lines)

    @contextmanager
    def write_element(self,
        element_: str,
        **attrs: str
    ) -> _ContextBlock[Self]:
        self._buffer.write('<')
        self._buffer.write(element_)
        for attr, value in attrs.items():
            self._buffer.write(f' {escape(attr)}="{escape(value)}"')
        self._buffer.write('>')
        yield self
        self._buffer.write('</')
        self._buffer.write(element_)
        self._buffer.write('>')


def render_html(vm: ViewModel) -> io.StringIO:
    buffer = io.StringIO()
    context = HtmlRenderContext(buffer)
    context.render(vm)
    return buffer


def html_renderer(
    vm_type: type[_TVM]
) -> Callable[[Renderer[_TVM]], Renderer[_TVM]]:
    def decorator(renderer: Renderer[_TVM]) -> Renderer[_TVM]:
        _renderers[vm_type] = renderer
        return renderer
    return decorator


@html_renderer(TextVM)
def render_text(vm: TextVM, ctx: HtmlRenderContext) -> None:
    ctx.write(escape(vm.text))


@html_renderer(ButtonVM)
def render_button(vm: ButtonVM, ctx: HtmlRenderContext) -> None:
    with ctx.write_element('button'):
        for item in vm.content:
            ctx.render(item)
