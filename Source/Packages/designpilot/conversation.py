from uuid import UUID, uuid4

import rxprop as rx
from litellm.types.utils import Delta

from .llm.llm import LLM
from .message import Message


class Conversation():
    def __init__(self, llm: LLM):
        self._llm = llm
        self._id = uuid4()

    @property
    def id(self) -> UUID:
        return self._id

    @rx.value
    def title(self) -> str:
        return "Untitled Conversation"

    @rx.value
    def messages(self) -> rx.ReactiveList[Message]:
        return rx.ReactiveList()

    async def submit_prompt(self, prompt: str|Delta) -> None:
        """
        Submits a prompt to the conversation and
        dispatches a completion request.
        """
        if isinstance(prompt, str):
            prompt = Delta(role='user', content=prompt)
        prompt_message = Message()
        prompt_message.raw_deltas.append(prompt)
        self.messages.append(prompt_message)
        history = list(m.merged_message for m in self.messages)
        
        message = Message()
        message.pending = True
        
        self.messages.append(message)
        async for delta in self._llm.stream_completion(history):
            message.raw_deltas.append(delta)
        message.pending = False
