import pytest

from app.core.config import settings
from app.services.llm.factory import get_llm_provider
from app.services.llm.fake_provider import FakeProvider
from app.services.llm.mistral_provider import MistralProvider


def test_factory_returns_fake_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "fake")
    assert isinstance(get_llm_provider(), FakeProvider)


def test_factory_returns_mistral_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    # A dummy key is enough here — MistralProvider's constructor only
    # checks that a key is *present*, it doesn't call the network. The
    # factory's job under test is picking the right class, not whether
    # that class can actually reach Mistral's API.
    monkeypatch.setattr(settings, "mistral_api_key", "dummy-key-for-test")
    monkeypatch.setattr(settings, "llm_provider", "mistral")
    assert isinstance(get_llm_provider(), MistralProvider)


def test_factory_toggles_correctly_between_providers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "mistral_api_key", "dummy-key-for-test")

    monkeypatch.setattr(settings, "llm_provider", "mistral")
    assert isinstance(get_llm_provider(), MistralProvider)

    monkeypatch.setattr(settings, "llm_provider", "fake")
    assert isinstance(get_llm_provider(), FakeProvider)

    monkeypatch.setattr(settings, "llm_provider", "mistral")
    assert isinstance(get_llm_provider(), MistralProvider)


def test_factory_rejects_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "nonexistent")
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        get_llm_provider()
