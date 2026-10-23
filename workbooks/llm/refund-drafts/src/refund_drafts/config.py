"""Configuration from the environment, validated at startup. Secrets are checked for presence, never printed."""
import math
import os
from dataclasses import dataclass


class ConfigError(ValueError):
    """Missing or invalid configuration; the program must not start half-configured."""


@dataclass(frozen=True)
class Settings:
    provider: str = "fake"          # "fake" (offline, default) or "openai" (paid, live)
    model: str | None = None        # Required for openai; deliberately no default model name
    attempt_timeout_s: float = 20.0  # Upper bound for one provider call
    total_deadline_s: float = 45.0   # Upper bound for all attempts of one draft, including backoff
    max_attempts: int = 3
    max_output_tokens: int = 400
    max_ticket_chars: int = 2000

    def __post_init__(self) -> None:
        if self.provider not in {"fake", "openai"}:
            raise ConfigError("REFUND_DRAFTS_PROVIDER must be 'fake' or 'openai'")
        if self.provider == "openai" and not self.model:
            raise ConfigError("Set OPENAI_MODEL to a model from your provider account; there is no default")
        for name in ("attempt_timeout_s", "total_deadline_s"):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0 < value <= 300:
                raise ConfigError(f"{name} must be in (0, 300] seconds")
        if self.attempt_timeout_s > self.total_deadline_s:
            raise ConfigError("attempt_timeout_s cannot exceed total_deadline_s")
        if not 1 <= self.max_attempts <= 5 or not 16 <= self.max_output_tokens <= 4000 or not 1 <= self.max_ticket_chars <= 20000:
            raise ConfigError("max_attempts must be 1-5, max_output_tokens 16-4000, max_ticket_chars 1-20000")


def _number(name: str, default: str, kind=float):
    try:
        return kind(os.environ.get(name, default))
    except ValueError as error:
        raise ConfigError(f"{name} must be a number") from error


def settings_from_env() -> Settings:
    provider = os.environ.get("REFUND_DRAFTS_PROVIDER", "fake").strip()
    if provider == "openai" and not os.environ.get("OPENAI_API_KEY", "").strip():
        raise ConfigError("OPENAI_API_KEY is not set; set it privately, never in a committed file")
    return Settings(provider=provider, model=os.environ.get("OPENAI_MODEL", "").strip() or None,
                    attempt_timeout_s=_number("REFUND_DRAFTS_ATTEMPT_TIMEOUT_S", "20"),
                    total_deadline_s=_number("REFUND_DRAFTS_TOTAL_DEADLINE_S", "45"),
                    max_attempts=_number("REFUND_DRAFTS_MAX_ATTEMPTS", "3", int),
                    max_output_tokens=_number("REFUND_DRAFTS_MAX_OUTPUT_TOKENS", "400", int))
