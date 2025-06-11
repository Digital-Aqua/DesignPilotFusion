from functools import cache
from pathlib import Path
from typing import Callable, Iterable

import jinja2 as j2

import designpilot_html
from designpilot.utils.resources import ResourceProvider


_template_dir = Path('templates')

class DpHtmlResourceProvider(ResourceProvider):
    def __init__(self):
        super().__init__(designpilot_html)

    @cache
    def read_text(self, name: str|Path) -> str:
        path = Path(name)
        if not path.suffix:
            path = _template_dir / path.with_suffix('.j2.html')
        return super().read_text.__wrapped__(self, path) # bypass underlying cache

    @property
    def default_css(self) -> str:
        return self.read_text("default.css")

    @property
    def default_js(self) -> str:
        return self.read_text("default.js")


class TemplateLoader(j2.BaseLoader):
    """
    Jinja2 loader that gets .j2.html files from `importlib.resources`.
    If resource_providers is not provided, uses a resource provider
    based on the `designpilot_html` package.
    """
    def __init__(self, resource_providers: Iterable[ResourceProvider] | None = None):
        self._resource_providers = list(
            resource_providers or (DpHtmlResourceProvider(),)
        )
    
    def cache_clear(self) -> None:
        """
        Clears the template cache for this loader.
        Useful during development to force-reload modified templates.
        """
        for provider in self._resource_providers:
            provider.read_text.cache_clear()

    def get_source(self,
        environment: j2.Environment,
        template: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        """
        Called by Jinja2 to get the source code for a template.
        Adds `templates/<template>.j2.html` if `template` has no extension.
        """
        for provider in self._resource_providers:
            try:
                source = provider.read_text(template)
                filename = template
                # rely on read_text's cache rather than j2's (clearable)
                up_to_date = lambda: False
                return source, filename, up_to_date
            except FileNotFoundError:
                pass
        return super().get_source(environment, template)
