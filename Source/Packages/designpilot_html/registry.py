import logging, os
from functools import reduce
from typing import (
    Any, Awaitable, Callable, Iterable, ParamSpec, TypeVar
)

from caseconverter import snakecase
from designpilot.ui.base import ViewModel
from designpilot.utils.resources import ResourceProvider
import jinja2 as j2
from markupsafe import Markup

from .resources import DpHtmlResourceProvider, TemplateLoader
from .template_functions import j2_functions


_log = logging.getLogger(__name__)


_P = ParamSpec('_P')
_T = TypeVar('_T')
_TVM = TypeVar('_TVM', bound=ViewModel)

AsyncCallable = Callable[_P, Awaitable[_T]]
Renderer = Callable[[_TVM], Iterable[Markup]]
StrPath = str | os.PathLike[str]


class HtmlRendererRegistry:
    """
    A registry of HTML view model renderers.

    This class is used to register view model renderers and templates.
    It is used to find the appropriate renderer for a given view model type,
    and to render a view model into HTML.
    """
    def __init__(self):
        self._renderers: dict[type[ViewModel], Renderer[Any]] = {}
    
    def register_renderer(self,
        vm_type: type[_TVM],
        renderer: Renderer[_TVM]
    ) -> Renderer[_TVM]:
        """
        Registers a renderer for a view model type.
        Returns the registered renderer.
        """
        self._renderers[vm_type] = renderer
        return renderer
    
    def get_renderer(self, vm_type: type[_TVM]) -> Renderer[_TVM] | None:
        """
        Gets the renderer for a view model type.
        Returns None if no renderer is found.
        """
        return self._renderers.get(vm_type, None)
    
    def clear_registry(self) -> None:
        """
        Clears the renderer cache.
        Useful during development to force-reload modified renderers.
        """
        self._renderers.clear()

    def render_as(self, vm_type: type[_TVM], *vms: _TVM) -> Iterable[Markup]:
        """
        Renders one or more view models into HTML,
        treating them explicitly as the given type.
        """
        renderer = self.get_renderer(vm_type)
        if not renderer:
            _log.warning(
                f"No renderer found for '{vm_type.__qualname__}'. Skipping."
            )
            return
        for vm in vms:
            yield from renderer(vm)

    def render(self, *vms: ViewModel) -> Iterable[Markup]:
        """
        Renders one or more view model into HTML.
        """
        for vm in vms:
            yield from self.render_as(type(vm), vm)


class JinjaHtmlRendererRegistry(HtmlRendererRegistry):
    """
    Extends `HtmlRendererRegistry` to provide a Jinja2 environment
    for rendering view templates.
    If `resource_loader` is not provided, uses a template loader and a
    resource provider based on the `designpilot_html` package.
    """
    def __init__(self,
        resource_loader: j2.BaseLoader|Iterable[ResourceProvider]|None = None
    ):
        super().__init__()
        if not isinstance(resource_loader, j2.BaseLoader):
            resource_loader = TemplateLoader(resource_loader)
        self._jinja_env = j2.Environment(
            autoescape = True,
            auto_reload = True,
            loader = resource_loader,
            finalize = self.finalise_j2_variable # type: ignore
        )
        self._jinja_env.globals.update(dict(
            **j2_functions,
            render_as = self.render_as,
        ))
    
    def finalise_j2_variable(self, *args: Any, **_) -> Any:
        """
        Jinja2 variable finaliser that renders a view model into HTML.
        If the object is a view model, it will be rendered using the
        registered renderer.
        If the object is not a view model, it will be returned unchanged.
        """
        try:
            obj = args[0]
        except IndexError:
            return None
        if isinstance(obj, ViewModel):
            renderer = self.get_renderer(type(obj))
            if renderer:
                items = renderer(obj)
                # Small allocation hit here, but no clear alternative.
                return reduce(lambda a, b: a + b, items, Markup(''))
        return obj

    def register_template(self,
        vm_type: type[_TVM],
        name: str | None = None
    ) -> Renderer[_TVM]:
        """
        Registers a template for a view model type.
        If `name` is not provided, uses the view model type's qualified name
        and converts it to snake_case (losing any trailing 'Vm').
        Returns the registered renderer.
        """
        if not name:
            # Auto-name, strip 'Vm' and convert to snake_case
            name = vm_type.__qualname__
            if name.endswith('Vm'):
                name = name[:-2]
            name = snakecase(name)
        template = self._jinja_env.get_template(name)
        def renderer(vm: _TVM) -> Iterable[Markup]:
            for item in template.generate(vm = vm):
                yield Markup(item)
        self.register_renderer(vm_type, renderer)
        return renderer


default_resource_provider = DpHtmlResourceProvider()
default_registry = JinjaHtmlRendererRegistry(
    resource_loader = (default_resource_provider,)
)
""" The default registry for DesignPilot HTML view model renderers. """
register_template = default_registry.register_template
register_renderer = default_registry.register_renderer
