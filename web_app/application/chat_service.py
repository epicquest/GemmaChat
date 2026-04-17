from __future__ import annotations

from collections.abc import Iterator

from domain.entities import Message
from domain.ports import ChatGateway


class ChatService:  # pylint: disable=too-few-public-methods
    """Application use-case: send a user message and stream the model's reply."""

    def __init__(self, gateway: ChatGateway) -> None:
        self._gateway = gateway

    def send(self, history: list[Message], user_message: Message) -> Iterator[str]:
        """
        Combine history + current user message and stream response tokens.

        Parameters
        ----------
        history:
            Previous messages (without the current user message).
        user_message:
            The new message just sent by the user (may contain images).
        """
        messages = history + [user_message]
        return self._gateway.stream(messages)
