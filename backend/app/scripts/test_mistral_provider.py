"""Manual smoke test for MistralProvider — requires a real MISTRAL_API_KEY
in backend/.env (get a free one at https://console.mistral.ai).

Usage (from backend/, with the venv active):
    python -m app.scripts.test_mistral_provider
"""

from app.services.llm.mistral_provider import MistralProvider


def main() -> None:
    provider = MistralProvider()
    reply = provider.generate(
        [{"role": "user", "content": "Reply with exactly the word: pong"}]
    )
    print("Model replied:", repr(reply))


if __name__ == "__main__":
    main()
