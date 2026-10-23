"""One draft, end to end: look up facts, build the request, call within budget, parse, validate, decide.

Every path ends in an Outcome; nothing about a provider failure reaches the agent as an exception.
`ready` is the only status whose draft may be shown as-is; `needs_agent` is a safe fallback, not a success.
"""
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from pydantic import ValidationError

from .config import Settings
from .domain import Records
from .prompt import PROMPT_VERSION, build_request
from .providers import PermanentProviderError, Provider, TransientProviderError
from .schema import DraftOut
from .validate import DEFAULT_CHECKS, Check, validate


@dataclass
class Outcome:
    ticket_id: str
    status: Literal["ready", "needs_agent", "failed"]
    reasons: list[str] = field(default_factory=list)
    draft: DraftOut | None = None
    attempts: int = 0
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    tokens_reported: bool = True

    def summary(self) -> dict:
        return {"ticket_id": self.ticket_id, "status": self.status, "reasons": self.reasons,
                "attempts": self.attempts, "prompt_version": self.prompt_version, "provider": self.provider,
                "model": self.model, "tokens": {"input": self.input_tokens, "output": self.output_tokens,
                                                "complete": self.tokens_reported},
                "draft": self.draft.model_dump(mode="json") if self.draft else None}


def draft_reply(ticket_id: str, records: Records, provider: Provider, settings: Settings, *,
                checks: tuple[Check, ...] = DEFAULT_CHECKS, prompt_version: str = PROMPT_VERSION,
                clock: Callable[[], float] = time.monotonic,
                sleep: Callable[[float], None] = time.sleep) -> Outcome:
    outcome = Outcome(ticket_id, "needs_agent", provider=provider.name)
    ticket = records.tickets.get(ticket_id)
    if ticket is None:
        outcome.status, outcome.reasons = "failed", ["unknown_ticket"]
        return outcome
    order = records.orders.get(ticket.order_id)
    if order is None:  # Never let the model guess about an order we cannot find.
        outcome.reasons = ["order_not_found"]
        return outcome
    if len(ticket.text) > settings.max_ticket_chars:
        outcome.reasons = ["ticket_too_long"]
        return outcome
    request = build_request(order, records.policies[order.payment_method], ticket, prompt_version)
    outcome.prompt_version = request.prompt_version

    deadline = clock() + settings.total_deadline_s
    for attempt in range(1, settings.max_attempts + 1):
        remaining = deadline - clock()
        if remaining <= 0:
            outcome.status, outcome.reasons = "failed", outcome.reasons + ["deadline_exceeded"]
            return outcome
        outcome.attempts = attempt
        try:
            result = provider.generate(request, timeout_s=min(settings.attempt_timeout_s, remaining),
                                       max_output_tokens=settings.max_output_tokens)
        except PermanentProviderError as error:
            outcome.status, outcome.reasons = "failed", outcome.reasons + [error.reason]
            return outcome
        except TransientProviderError as error:
            outcome.reasons.append(error.reason)
            if attempt < settings.max_attempts:
                backoff = min(2.0 ** (attempt - 1), max(0.0, deadline - clock()))
                sleep(backoff)
            continue
        outcome.model = result.model
        if result.input_tokens is None or result.output_tokens is None:
            outcome.tokens_reported = False
        outcome.input_tokens += result.input_tokens or 0
        outcome.output_tokens += result.output_tokens or 0
        if result.status == "incomplete":
            outcome.reasons.append(f"incomplete:{result.detail}")
            return outcome  # Same limits would truncate again; hand to an agent instead of retrying.
        if result.status == "refused":
            outcome.reasons.append("refused")
            return outcome
        try:
            draft = DraftOut.from_json(result.text or "")
        except ValidationError:
            outcome.reasons.append("malformed_output")
            continue  # Sampling may produce valid output next time; still inside the same budget.
        outcome.draft = draft
        problems = validate(draft, order, checks)
        if problems:
            outcome.reasons += problems
            return outcome
        if draft.needs_agent:
            outcome.reasons.append("model_abstained")
            return outcome
        outcome.status = "ready"
        return outcome
    outcome.status = "failed"
    outcome.reasons.append("attempts_exhausted")
    return outcome
