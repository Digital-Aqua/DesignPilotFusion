from typing import AsyncIterable, Iterable, Protocol, runtime_checkable

import litellm as ll
from litellm.types.utils import ModelResponseStream
from litellm.types.utils import Delta, Message as MessageData


@runtime_checkable
class LLMConfigPattern(Protocol):
    @property
    def model(self) -> str: ...


class LLM():
    def __init__(self, config: LLMConfigPattern):
        self._config = config

    def completion(self,
        messages: Iterable[MessageData]
    ) -> AsyncIterable[ModelResponseStream]:
        messages = list(messages)
        print("Messages:", len(messages))
        for m in messages:
            print(m)
        return ll.completion(  # type: ignore
            model=self._config.model,
            messages=list(messages),
            stream=True
        )

    async def stream_completion(self,
        history: Iterable[MessageData]
    ) -> AsyncIterable[Delta]:
        """
        Streams a completion and extends the conversation with responses.
        """
        async for result in self.completion(history):
            for choice in result.choices:
                yield choice.delta
