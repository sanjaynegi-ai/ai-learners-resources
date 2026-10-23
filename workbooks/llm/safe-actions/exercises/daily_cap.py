"""Independent exercise: a per-tenant daily cap on goodwill credits.

Requirement from Finance:
  * The total of goodwill credits a tenant has recorded today (any status: pending_approval, queued, done or
    failed, because a failed one may still have been applied) plus the new credit must not exceed
    DAILY_CAP_CENTS. Otherwise return ["daily_cap_exceeded"].
  * Other tools are unaffected: return [].
  * A replay of an already-recorded credit (same idempotency key) must NOT be rejected by the cap; the
    executor will report it as a duplicate. Count only what would be new.
  * Never trust anything in `args` except the amount being requested.

Signature matches executor.propose_and_record(extra_checks=...). Use store.db for queries, and
safe_actions.executor.idempotency_key to recognize a replay. "Today" is the current UTC date.
Do not open daily_cap_reference.py until you have recorded your own attempt.
"""
from safe_actions.store import Principal, Store

DAILY_CAP_CENTS = 6000


def check_daily_cap(store: Store, principal: Principal, ticket_id: str, tool: str, args: dict) -> list[str]:
    # TODO 1: ignore tools other than "issue_goodwill_credit".
    # TODO 2: if this exact action is already recorded (same idempotency key), return [].
    # TODO 3: sum today's recorded credits for principal.tenant and compare with DAILY_CAP_CENTS.
    raise NotImplementedError("Implement check_daily_cap")
