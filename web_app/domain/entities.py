from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # "user" | "assistant"
    content: str
    images: list[bytes] = field(default_factory=list)


@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)

    def add(self, message: Message) -> None:
        self.messages.append(message)

    @staticmethod
    def from_session(raw: list[dict]) -> "Conversation":
        """Deserialise history stored in the HTTP session (no images)."""
        messages = [Message(role=m["role"], content=m["content"]) for m in raw]
        return Conversation(messages=messages)

    def to_session(self) -> list[dict]:
        """Serialise to a JSON-safe list for storage in the HTTP session."""
        return [{"role": m.role, "content": m.content} for m in self.messages]
