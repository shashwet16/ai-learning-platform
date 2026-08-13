from abc import ABC, abstractmethod
from typing import Literal, TypedDict


class ChatMessage(TypedDict):
    """One turn in a conversation, in the shape every LLM vendor's chat
    API expects. Named `ChatMessage`, not `Message`, to avoid confusion
    with the future `Message` ORM model (see M4.4) — this type never
    touches the database, it's purely the shape passed to a provider.
    """

    role: Literal["user", "assistant", "system"]
    content: str


class LLMProvider(ABC):
    """Provider-agnostic contract for generating a chat completion.

    Every LLM vendor integration (Anthropic, OpenAI, ...) implements this
    interface so the rest of the application — the chat endpoint, the
    provider factory — never has to know or care which vendor is actually
    configured. No vendor-specific code belongs in this file.
    """

    @abstractmethod
    def generate(self, messages: list[ChatMessage]) -> str:
        """Given the conversation so far, return the assistant's reply text."""
        raise NotImplementedError
