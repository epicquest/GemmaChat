from __future__ import annotations

import base64
from collections.abc import Iterator

import ollama

from domain.entities import Message
from domain.ports import ChatGateway

MODEL = "gemma4:e2b"


class OllamaGateway(ChatGateway):
    """Adapter that implements ChatGateway using a local Ollama server."""

    def __init__(self, model: str = MODEL) -> None:
        self._model = model

    def stream(self, messages: list[Message]) -> Iterator[str]:
        ollama_messages = [self._serialise(m) for m in messages]
        response = ollama.chat(
            model=self._model,
            messages=ollama_messages,
            stream=True,
        )
        for chunk in response:
            yield chunk.message.content or ""

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _serialise(message: Message) -> dict:
        payload: dict = {"role": message.role, "content": message.content}
        if message.images:
            payload["images"] = [
                base64.b64encode(img).decode() for img in message.images
            ]
        return payload
