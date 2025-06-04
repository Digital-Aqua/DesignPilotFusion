import logging
from typing import Any, Protocol, runtime_checkable

import rxprop as rx

from .conversation import Conversation
from .llm.llm import LLM, LLMConfigPattern

__all__ = [ "DpApp" ]


@runtime_checkable
class DpAppConfigPattern(
    LLMConfigPattern,
    Protocol
):
    pass


class DpApp(object):

    def __init__(self, *,
        debug: bool = False,
        config: DpAppConfigPattern,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._debug = debug
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(logging.DEBUG if self._debug else logging.INFO)
        self._config = config
        self._llm = LLM(config=config)


    @rx.value
    def conversations(self) -> rx.ReactiveList[Conversation]:
        return rx.ReactiveList()


    def create_conversation(self) -> Conversation:
        new_conversation = Conversation(llm=self._llm)
        self.conversations.append(new_conversation)
        return new_conversation


    async def run(self) -> None:
        raise NotImplementedError("TODO")


    async def stop(self) -> None:
        raise NotImplementedError("TODO")

