from app.services.llm.base import ChatMessage, LLMProvider


class FakeProvider(LLMProvider):
    """Deterministic, network-free provider for tests and local dev
    without an API key — echoes the last user message back with a fixed
    prefix instead of calling any real LLM.
    """

    def generate(self, messages: list[ChatMessage]) -> str:
        last_message = messages[-1]["content"] if messages else ""
        return f"[fake response] {last_message}"
