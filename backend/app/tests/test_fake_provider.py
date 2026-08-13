from app.services.llm.fake_provider import FakeProvider


def test_fake_provider_echoes_last_message() -> None:
    provider = FakeProvider()
    reply = provider.generate([{"role": "user", "content": "hello there"}])
    assert reply == "[fake response] hello there"


def test_fake_provider_handles_empty_messages() -> None:
    provider = FakeProvider()
    assert provider.generate([]) == "[fake response] "
