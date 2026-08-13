from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.fake_provider import FakeProvider
from app.services.llm.mistral_provider import MistralProvider

_PROVIDERS: dict[str, type[LLMProvider]] = {
    "mistral": MistralProvider,
    "fake": FakeProvider,
}


def get_llm_provider() -> LLMProvider:
    try:
        provider_cls = _PROVIDERS[settings.llm_provider]
    except KeyError:
        raise ValueError(
            f"Unknown LLM_PROVIDER {settings.llm_provider!r}. "
            f"Registered providers: {sorted(_PROVIDERS)}"
        ) from None
    return provider_cls()
