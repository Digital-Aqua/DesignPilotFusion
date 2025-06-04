from typing import Any, Iterable, Mapping
from uuid import UUID

import rxprop as rx

from ..dpapp import DpApp
from ..conversation import Conversation
from ..message import Message
from .base import ViewModel, ViewModelRef
from .utils import MarkdownString


class ChatMessageVm(ViewModelRef[Message]):

    @rx.computed
    def role(self) -> str:
        return self._model.merged_message.role

    @rx.computed
    def pending(self) -> bool:
        return self._model.pending

    @rx.computed
    def content(self) -> MarkdownString:
        return MarkdownString(self._model.merged_message.content or '')


class ChatConversationVm(
    ViewModelRef[Conversation]
):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @property
    def id(self) -> UUID:
        return self._model.id

    @rx.computed
    def title(self) -> str:
        return self._model.title

    @rx.computed
    def messages(self) -> Iterable[ChatMessageVm]:
        return [
            ChatMessageVm(model=m)
            for m in self._model.messages
        ]


class ChatVm(ViewModel):
    def __init__(self, app: DpApp, **kwargs: Any):
        super().__init__(**kwargs)
        self._app = app

    @rx.computed
    def conversation_ids(self) -> Mapping[UUID, str]:
        return {
            c.id: c.title
            for c in self._app.conversations
        }

    @rx.value
    def conversation(self) -> ChatConversationVm|None:
        return None

    def select_conversation(self, conversation_id: UUID) -> None:
        for c in self._app.conversations:
            if c.id == conversation_id:
                self.conversation = ChatConversationVm(model=c)
                return
        self.conversation = None
    
    def new_conversation(self) -> None:
        new_conversation = self._app.create_conversation()
        self.select_conversation(new_conversation.id)
