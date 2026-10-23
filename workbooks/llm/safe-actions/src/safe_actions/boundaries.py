"""Fault-injectable boundaries on both sides of the application.

ProposalProvider stands in for a model's tool-calling output: its arguments are untrusted JSON text.
FakeService stands in for an external system (email, payment credits) that honors idempotency keys,
like payment APIs that accept an Idempotency-Key header. Both can be scripted to fail in realistic ways.
"""
import itertools
import json
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ToolCall:
    call_id: str      # Generated per proposal by the provider; NOT stable across duplicate proposals
    name: str
    arguments: str    # Raw JSON text exactly as the model produced it


class ProviderTimeout(Exception):
    pass


class ProposalProvider(Protocol):
    def propose(self, ticket_id: str) -> ToolCall: ...


_ids = itertools.count(1)


def call(name: str, arguments: dict | str) -> ToolCall:
    """Build a proposal as a model would: a fresh call_id every time, arguments as JSON text."""
    text = arguments if isinstance(arguments, str) else json.dumps(arguments)
    return ToolCall(f"call_{next(_ids):04d}", name, text)


@dataclass
class FakeProposalProvider:
    """Returns scripted proposals in order; the string "timeout" raises ProviderTimeout instead."""
    script: list[ToolCall | str] = field(default_factory=list)
    calls: int = 0

    def propose(self, ticket_id: str) -> ToolCall:
        self.calls += 1
        item = self.script.pop(0)
        if item == "timeout":
            raise ProviderTimeout("timeout")
        return item


class ServiceError(Exception):
    """The external system rejected or failed the request; it did not apply the effect."""


class ServiceTimeout(Exception):
    """No answer arrived. The effect may or may not have been applied: the ambiguous case."""


@dataclass
class FakeService:
    """An external system that deduplicates by idempotency key. Faults per call, in order:
    "ok", "error", "timeout_before" (not applied), "timeout_after" (applied, but the caller never hears)."""
    name: str
    script: list[str] = field(default_factory=list)
    applied: dict[str, str] = field(default_factory=dict)
    effects: int = 0      # Real-world effects: emails sent, credits issued
    calls: int = 0

    def apply(self, idempotency_key: str, payload: dict) -> str:
        self.calls += 1
        fault = self.script.pop(0) if self.script else "ok"
        if fault == "error":
            raise ServiceError(f"{self.name}: 503")
        if fault == "timeout_before":
            raise ServiceTimeout(f"{self.name}: timeout")
        if idempotency_key in self.applied:
            return self.applied[idempotency_key]  # Same key, same answer, no second effect
        result = f"{self.name}-{len(self.applied) + 1:04d}"
        self.applied[idempotency_key] = result
        self.effects += 1
        if fault == "timeout_after":
            raise ServiceTimeout(f"{self.name}: timeout after applying")
        return result
