from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from .entities import Message


class ChatGateway(ABC):
    """Port that the application layer uses to communicate with an LLM backend."""

    @abstractmethod
    def stream(self, messages: list[Message]) -> Iterator[str]:
        """Yield text tokens as they arrive from the model."""
        ...
