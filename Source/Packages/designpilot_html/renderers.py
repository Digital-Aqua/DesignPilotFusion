from typing import Iterable

from markdown_it import MarkdownIt
from markupsafe import Markup

from designpilot.ui import EmptyVm
from designpilot.ui.basic import MarkdownVm


_empty_iter = iter(())
def empty_renderer(vm: EmptyVm) -> Iterable[Markup]:
    """
    Renders an empty view model into HTML.
    """
    return _empty_iter


default_markdown_parser = (
    MarkdownIt('commonmark', dict(
        breaks = True,
        html = True
    ))
    .enable('table')
)
""" The default markdown parser for DesignPilot. """


def render_markdown(vm: MarkdownVm) -> Iterable[Markup]:
    """
    Renders markdown into HTML.
    """
    yield Markup(default_markdown_parser.render(vm.content))

