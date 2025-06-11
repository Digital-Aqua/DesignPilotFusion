from typing import Any, Iterable, Mapping
from uuid import UUID

import rxprop as rx

from ..dpapp import DpApp
from ..conversation import Conversation
from ..message import Message
from .base import ViewModelRef
from .basic import MarkdownVm


class ChatMessageVm(ViewModelRef[Message]):
    @rx.computed
    def role(self) -> str:
        return self._model.merged_message.role

    @rx.computed
    def pending(self) -> bool:
        return self._model.pending

    @rx.computed
    def content(self) -> MarkdownVm:
        return MarkdownVm(self._model.merged_message.content or '')


class ChatConversationVm(ViewModelRef[Conversation]):
    @rx.computed
    def title(self) -> str:
        return self._model.title

    @rx.computed
    def id(self) -> str:
        return self._model.id.hex

    @rx.computed
    def messages(self) -> Iterable[ChatMessageVm]:
        return [
            ChatMessageVm(model=message)
            for message in self._model.messages
        ]


class ChatVm(ViewModelRef[DpApp]):
    @rx.computed
    def app(self) -> DpApp:
        return self._model

    @rx.computed
    def conversation_map(self) -> Mapping[UUID, str]:
        return {
            c.id: c.title
            for c in self._model.conversations
        }

    @rx.value
    def selected_conversation_id(self) -> UUID:
        if self._model.conversations:
            return self._model.conversations[-1].id
        return UUID(int=0)

    @rx.computed
    def selected_conversation(self) -> ChatConversationVm|None:
        try:
            id = self.selected_conversation_id
            conversation = next(iter(
                c for c in self._model.conversations
                if c.id == id
            ))
            return ChatConversationVm(model=conversation)
        except StopIteration:
            return None

    def new_conversation(self, **__: Any) -> None:
        new_conversation = self._model.create_conversation()
        self.select_conversation(new_conversation.id)

    def select_conversation(self, conversation_id: UUID|str) -> None:
        if isinstance(conversation_id, str):
            conversation_id = UUID(conversation_id)
        for c in self._model.conversations:
            if c.id == conversation_id:
                self.selected_conversation_id = c.id
                return
        raise ValueError(f"Conversation {conversation_id} not found")
