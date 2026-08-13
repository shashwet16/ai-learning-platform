from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # No default on purpose: every deployment must explicitly declare which
    # environment it's running in rather than silently falling back to one.
    environment: Literal["development", "staging", "production"]

    # No default: the app can't run at all without a database to talk to.
    database_url: str

    # No default on purpose: a JWT secret must never silently fall back to
    # a value shared across every deployment.
    jwt_secret: str
    jwt_expire_minutes: int = 30

    # Optional, unlike the settings above: nothing in the app depends on
    # this yet (no route calls an LLM provider until M4.5), so the app
    # must still be able to start without it. MistralProvider itself
    # fails fast if it's missing at the point it's actually instantiated.
    mistral_api_key: str | None = None

    # Which registered LLMProvider get_llm_provider() returns. Kept as a
    # plain str, not a Literal of provider names — the factory module
    # (services/llm/factory.py) is the single place that owns the actual
    # registry, so config.py doesn't need to know every provider name.
    llm_provider: str = "mistral"

    app_name: str = "AI Engineering Learning Platform API"


settings = Settings()
