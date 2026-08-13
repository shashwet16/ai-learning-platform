from mistralai.client import Mistral

from app.core.config import settings
from app.services.llm.base import ChatMessage, LLMProvider


class MistralProvider(LLMProvider):
    """LLMProvider backed by Mistral AI's chat completion API."""

    def __init__(self, model: str = "mistral-small-latest") -> None:
        if not settings.mistral_api_key:
            raise RuntimeError(
                "MISTRAL_API_KEY is not set — required to use MistralProvider."
            )
        self._client = Mistral(api_key=settings.mistral_api_key)
        self._model = model

    def generate(self, messages: list[ChatMessage]) -> str:
        response = self._client.chat.complete(
            model=self._model,
            messages=list(messages),
        )
        content = response.choices[0].message.content
        if not isinstance(content, str):
            raise RuntimeError(
                "Mistral API returned non-text content; expected a plain string."
            )
        return content
