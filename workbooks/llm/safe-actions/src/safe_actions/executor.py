"""From an untrusted proposal to a durable, idempotent effect.

    propose_and_record: model proposal -> registry -> strict arguments -> role -> business rules -> approval rule
                        -> one durable action row (the outbox entry), keyed by content, not by call_id
    approve:            a different supervisor in the same tenant releases a pending action
    dispatch:           sends queued actions to external services with the action key as idempotency key;
                        ambiguous timeouts are retried with the same key; crashes are recovered on the next run
"""
import hashlib
import json
from dataclasses import dataclass, field

from pydantic import ValidationError

from .boundaries import FakeService, ProposalProvider, ProviderTimeout, ServiceError, ServiceTimeout
from .store import Principal, Store
from .tools import TOOLS


@dataclass
class Decision:
    status: str  # queued | pending_approval | duplicate | rejected | provider_failed
    action_key: str | None = None
    reasons: list[str] = field(default_factory=list)


class SimulatedCrash(Exception):
    """Stands in for the process dying at an inconvenient moment."""


def idempotency_key(tenant: str, ticket_id: str, tool: str, args: dict) -> str:
    """Derived from what the action *is*, so a repeated proposal maps to the same key.
    A provider's call_id is unique per proposal and would turn every duplicate into a new action."""
    canonical = json.dumps({"tenant": tenant, "ticket": ticket_id, "tool": tool, "args": args}, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]


def propose_and_record(store: Store, principal: Principal, ticket_id: str, provider: ProposalProvider,
                       max_attempts: int = 2, extra_checks=()) -> Decision:
    """`extra_checks` are callables (store, principal, ticket_id, tool_name, args_dict) -> problem codes, run last."""
    for _ in range(max_attempts):
        try:
            proposal = provider.propose(ticket_id)
            break
        except ProviderTimeout:
            continue
    else:
        return Decision("provider_failed", reasons=["provider_timeout"])

    spec = TOOLS.get(proposal.name)
    if spec is None:
        return Decision("rejected", reasons=["unknown_tool"])
    try:
        args = spec.args.model_validate_json(proposal.arguments)
    except ValidationError as error:
        return Decision("rejected", reasons=sorted({f"invalid_argument:{'.'.join(map(str, e['loc'])) or 'json'}:{e['type']}"
                                                    for e in error.errors()}))
    if principal.role not in spec.roles:
        return Decision("rejected", reasons=["role_not_allowed"])
    problems = spec.check(store, principal, ticket_id, args)
    if problems:
        return Decision("rejected", reasons=problems)

    payload = args.model_dump()
    problems = [problem for check in extra_checks for problem in check(store, principal, ticket_id, spec.name, payload)]
    if problems:
        return Decision("rejected", reasons=problems)
    key = idempotency_key(principal.tenant, ticket_id, spec.name, payload)
    status = "pending_approval" if spec.needs_approval(args) else "queued"
    existing = store.record_action(key, principal, ticket_id, spec.name, payload, status)
    if existing is not None:
        return Decision("duplicate", key, [f"already_{existing}"])
    return Decision(status, key)


def approve(store: Store, approver: Principal, key: str) -> bool:
    action = store.action(key)
    if action is None or approver.role != "supervisor" or approver.tenant != action["tenant"]:
        return False
    if approver.user == action["actor"]:
        return False  # Separation of duties: nobody approves their own request
    return store.add_approval(key, approver.user)


@dataclass
class DispatchReport:
    done: int = 0
    retry_later: int = 0
    failed: int = 0


def dispatch(store: Store, services: dict[str, FakeService], *, max_attempts: int = 3,
             crash_after_effect: bool = False) -> DispatchReport:
    """One pass over the outbox. Safe to run again at any time, including after a crash."""
    report = DispatchReport()
    for key in store.queued():
        action = store.action(key)
        spec = TOOLS[action["tool"]]
        if spec.service is None:  # Internal action: recording it is the effect.
            store.finish(key, "done", "recorded")
            report.done += 1
            continue
        attempts = store.count_attempt(key)  # Durable before the call: a crash still counts the attempt
        try:
            result = services[spec.service].apply(key, action["args"])
        except (ServiceError, ServiceTimeout):
            if attempts >= max_attempts:
                store.finish(key, "failed", "needs_reconciliation")  # A person checks the external system
                report.failed += 1
            else:
                report.retry_later += 1
            continue
        if crash_after_effect:
            raise SimulatedCrash(f"crashed after {spec.service} applied {key[:8]}")
        store.finish(key, "done", result)
        report.done += 1
    return report
