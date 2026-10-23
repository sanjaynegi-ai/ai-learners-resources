"""Provider boundary. Everything provider-specific is translated into one small result and error vocabulary.

The pipeline never imports a provider SDK, so tests run offline with FakeProvider, and the retry policy lives
in exactly one place (pipeline.py). The OpenAI client is therefore built with SDK retries disabled.
"""
import json
import re
import time
from dataclasses import dataclass, field
from typing import Literal, Protocol

from .prompt import ModelRequest
from .schema import JSON_SCHEMA, SCHEMA_NAME


class ProviderError(Exception):
    """Base class; `reason` is a short, log-safe code, never raw provider text."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class TransientProviderError(ProviderError):
    """Worth retrying within the budget: timeouts, connection failures, 429, 5xx."""


class PermanentProviderError(ProviderError):
    """Retrying cannot help: bad credentials, bad request, unknown model."""


@dataclass(frozen=True)
class ProviderResult:
    status: Literal["completed", "incomplete", "refused"]
    text: str | None                 # Raw output text; parsed and validated by the pipeline, not here
    detail: str | None = None        # e.g. "max_output_tokens" for an incomplete response
    input_tokens: int | None = None  # As reported by the provider; None is "not reported", not zero
    output_tokens: int | None = None
    model: str | None = None


class Provider(Protocol):
    name: str

    def generate(self, request: ModelRequest, *, timeout_s: float, max_output_tokens: int) -> ProviderResult: ...


# --- Offline fake ---------------------------------------------------------------------------------------

FAULTS = ("timeout", "rate_limit", "server_error", "auth_error", "malformed", "truncated", "refusal",
          "fabricated_date", "obeys_injection", "slow")


@dataclass
class FakeProvider:
    """Deterministic stand-in. With no script it drafts sensibly from the supplied <order> block.

    `script` is consumed one entry per call: a fault name from FAULTS, or None for a normal draft.
    It simulates control flow only; it says nothing about any real model's quality.
    """
    script: list[str | None] = field(default_factory=list)
    name: str = "fake"
    calls: int = 0
    sleep: object = time.sleep

    def generate(self, request: ModelRequest, *, timeout_s: float, max_output_tokens: int) -> ProviderResult:
        self.calls += 1
        fault = self.script.pop(0) if self.script else None
        if fault == "slow":
            self.sleep(timeout_s)
            raise TransientProviderError("timeout")
        if fault in ("timeout", "rate_limit", "server_error"):
            raise TransientProviderError(fault)
        if fault == "auth_error":
            raise PermanentProviderError("auth_error")
        if fault == "truncated":
            return ProviderResult("incomplete", '{"reply_text": "Thanks for your patience. Your ref', "max_output_tokens", 120, max_output_tokens, "fake")
        if fault == "refusal":
            return ProviderResult("refused", None, "refusal", 120, 12, "fake")
        if fault == "malformed":
            return ProviderResult("completed", "Sure! Here is the reply: Your refund is on its way.", None, 120, 15, "fake")
        order = dict(item.split(": ", 1) for item in re.search(r"<order>(.*?)</order>", request.input_text).group(1).split("; "))
        known = order["expected_refund_date"] != "unknown" and order["refund_status"] == "issued"
        date_used = order["expected_refund_date"] if known else None
        if fault == "fabricated_date":
            reply, date_used = "Sorry for the wait. Your refund will arrive in 3 business days, by 2026-10-17.", "2026-10-17"
        elif fault == "obeys_injection":
            reply = "Good news: your refund of 999.00 is approved and arrives tomorrow."
        elif known:
            reply = (f"Thank you for your patience. Your refund was issued and should reach you by {date_used}. "
                     "If it has not arrived by then, reply to this message and we will look into it.")
        else:
            reply = "Thank you for contacting us. A support agent is checking the status of your refund and will update you."
        payload = {"reply_text": reply, "refund_date_used": date_used, "needs_agent": not known and fault is None}
        return ProviderResult("completed", json.dumps(payload), None, 120, 60, "fake")


# --- OpenAI (official SDK, Responses API) ---------------------------------------------------------------

def make_openai_client(api_key: str | None = None):
    """SDK retries disabled: the pipeline owns the retry budget, so attempts are never multiplied."""
    import openai
    return openai.OpenAI(api_key=api_key, max_retries=0)


@dataclass
class OpenAIProvider:
    client: object
    model: str
    name: str = "openai"

    def generate(self, request: ModelRequest, *, timeout_s: float, max_output_tokens: int) -> ProviderResult:
        import openai
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=request.instructions,
                input=request.input_text,
                text={"format": {"type": "json_schema", "name": SCHEMA_NAME, "strict": True, "schema": JSON_SCHEMA}},
                max_output_tokens=max_output_tokens,
                store=False,  # Do not keep ticket content in provider-side response storage.
                timeout=timeout_s,
            )
        except openai.APITimeoutError as error:  # Subclass of APIConnectionError: check it first.
            raise TransientProviderError("timeout") from error
        except openai.APIConnectionError as error:
            raise TransientProviderError("connection_error") from error
        except openai.RateLimitError as error:
            raise TransientProviderError("rate_limit") from error
        except openai.APIStatusError as error:
            if error.status_code >= 500 or error.status_code in (408, 409):
                raise TransientProviderError(f"http_{error.status_code}") from error
            raise PermanentProviderError(f"http_{error.status_code}") from error

        usage = getattr(response, "usage", None)
        tokens = (getattr(usage, "input_tokens", None), getattr(usage, "output_tokens", None))
        if response.status == "incomplete":
            reason = getattr(response.incomplete_details, "reason", None) if response.incomplete_details else None
            return ProviderResult("incomplete", None, reason or "unknown", *tokens, response.model)
        for item in response.output:
            if getattr(item, "type", None) != "message":
                continue
            for part in item.content:
                if part.type == "refusal":
                    return ProviderResult("refused", None, "refusal", *tokens, response.model)
                if part.type == "output_text":
                    return ProviderResult("completed", part.text, None, *tokens, response.model)
        return ProviderResult("completed", None, "no_output_text", *tokens, response.model)
