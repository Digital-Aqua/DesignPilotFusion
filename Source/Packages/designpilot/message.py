from functools import reduce

from litellm.types.utils import Delta, Message as MessageData
import rxprop as rx


def _add_delta(message: MessageData, delta: Delta) -> MessageData:
    """
    Creates a new MessageData by merging the existing message with a Delta.
    """
    return MessageData(
        content = (
            (message.content or '') + str(delta.content or '') # type: ignore
        ) or '',
        role = str(delta.role) if delta.role else message.role, # type: ignore
        function_call = (
            getattr(message, 'function_call', None)
            or getattr(delta, 'function_call', None)
        ) or None,
        tool_calls = (
            (getattr(message, 'tool_calls', None) or [])
            + (getattr(delta, 'tool_calls', None) or [])
        ) or None,
        audio = (
            getattr(message, 'audio', None)
            or getattr(delta, 'audio', None)
        ) or None,
        provider_specific_fields = (
            (getattr(message, 'provider_specific_fields', None) or {}) # type: ignore
            | (getattr(delta, 'provider_specific_fields', None) or {}) # type: ignore
        ) or None,
        reasoning_content = (
            (getattr(message, 'reasoning_content', None) or '')
            + (getattr(delta, 'reasoning_content', None) or '')
        ) or None,
        thinking_blocks = (
            (getattr(message, 'thinking_blocks', None) or []) # type: ignore
            + (getattr(delta, 'thinking_blocks', None) or []) # type: ignore
        ) or None,
        annotations = (
            (getattr(message, 'annotations', None) or []) # type: ignore
            + (getattr(delta, 'annotations', None) or []) # type: ignore
        ) or None
    )


class Message():
    @rx.value
    def pending(self) -> bool:
        return False

    @rx.value
    def raw_deltas(self) -> rx.ReactiveList[Delta]:
        return rx.ReactiveList()

    @rx.computed
    def merged_message(self) -> MessageData:
        return reduce(
            _add_delta,
            self.raw_deltas,
            MessageData(role='') # type: ignore
        )
