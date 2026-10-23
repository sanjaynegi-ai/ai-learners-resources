import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Role = Literal["agent", "supervisor"]


class ConfigError(ValueError):
    """Startup configuration is missing or invalid; the service must not start half-configured."""


@dataclass(frozen=True)
class Principal:
    """Identity established by trusted server code, never by the request body."""
    tenant: str
    role: Role


@dataclass(frozen=True)
class Settings:
    principals: dict[str, Principal]  # SHA-256 hex digest of a bearer token -> principal
    triage_timeout: float = 0.5

    def __post_init__(self) -> None:
        if not self.principals:
            raise ConfigError("At least one principal is required")
        timeout = self.triage_timeout
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 10:
            raise ConfigError("Triage timeout must be a finite number of seconds in (0, 10]")

    def authenticate(self, token: str) -> Principal | None:
        return self.principals.get(hashlib.sha256(token.encode("utf-8")).hexdigest())


def load_principals(path: Path) -> dict[str, Principal]:
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigError(f"Cannot read principals file: {type(error).__name__}") from error
    if not isinstance(rows, list):
        raise ConfigError("Principals file must contain a list")
    principals: dict[str, Principal] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"token_sha256", "tenant", "role"}:
            raise ConfigError("Each principal needs exactly token_sha256, tenant and role")
        digest, tenant, role = row["token_sha256"], row["tenant"], row["role"]
        if not isinstance(digest, str) or len(digest) != 64 or digest in principals:
            raise ConfigError("Principal digests must be unique 64-character SHA-256 hex strings")
        if not isinstance(tenant, str) or not tenant or role not in ("agent", "supervisor"):
            raise ConfigError("Principal tenant must be nonempty and role must be agent or supervisor")
        principals[digest] = Principal(tenant, role)
    return principals


def load_settings_from_env() -> Settings:
    path = os.environ.get("QUICKCART_PRINCIPALS_FILE")
    if not path:
        raise ConfigError("QUICKCART_PRINCIPALS_FILE is not set; see .env.example")
    raw_timeout = os.environ.get("QUICKCART_TRIAGE_TIMEOUT_SECONDS", "0.5")
    try:
        timeout = float(raw_timeout)
    except ValueError as error:
        raise ConfigError("QUICKCART_TRIAGE_TIMEOUT_SECONDS must be a number") from error
    return Settings(load_principals(Path(path)), timeout)
