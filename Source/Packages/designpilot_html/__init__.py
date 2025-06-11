from .view import View

__all__ = [
    'View',
]

from .registry import register_template, register_renderer
from .renderers import render_markdown, empty_renderer

import designpilot.ui.base as base
register_renderer(base.EmptyVm, empty_renderer)
register_template(base.ContentVm)

import designpilot.ui.basic as basic
register_template(basic.TextVm)
register_renderer(basic.MarkdownVm, render_markdown)
register_template(basic.ExpanderVm)

import designpilot.ui.chat as chat
register_template(chat.ChatVm)
# register_template(chat.ChatConversationVm)
# register_template(chat.ChatMessageVm)

import designpilot.ui.root as root
register_template(root.RootVm)

#import designpilot.ui.settings as settings

import designpilot.ui.tabs as tabs
register_template(tabs.TabContainerVm)
