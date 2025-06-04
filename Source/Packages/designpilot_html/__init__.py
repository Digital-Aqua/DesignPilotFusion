from .view import *

from .renderers import register_template

import designpilot.ui.base as base
register_template(base.ContentVm, 'content.j2.html')

import designpilot.ui.basic as basic
register_template(basic.TextVm, 'text.j2.html')
register_template(basic.ButtonVm, 'button.j2.html')

import designpilot.ui.root as root
register_template(root.TabContainerVm, 'tab_container.j2.html')
register_template(root.RootVm, 'root.j2.html')

import designpilot.ui.chat as chat
register_template(chat.ChatVm, 'chat.j2.html')
register_template(chat.ChatConversationVm, 'conversation.j2.html')
register_template(chat.ChatMessageVm, 'message.j2.html')