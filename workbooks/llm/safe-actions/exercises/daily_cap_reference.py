"""Inspectable reference for the daily cap. Consulting it is disclosed assistance, not independent evidence."""
from safe_actions.executor import idempotency_key
from safe_actions.store import Principal, Store

DAILY_CAP_CENTS = 6000


def check_daily_cap(store: Store, principal: Principal, ticket_id: str, tool: str, args: dict) -> list[str]:
    if tool != "issue_goodwill_credit":
        return []
    if store.action(idempotency_key(principal.tenant, ticket_id, tool, args)) is not None:
        return []  # A replay: the executor reports it as a duplicate; it adds nothing new.
    spent = store.db.execute(
        "SELECT COALESCE(SUM(json_extract(args, '$.amount_cents')), 0) FROM actions "
        "WHERE tenant = ? AND tool = 'issue_goodwill_credit' "
        "AND date(created_at, 'unixepoch') = date('now')",
        (principal.tenant,)).fetchone()[0]
    return ["daily_cap_exceeded"] if spent + args["amount_cents"] > DAILY_CAP_CENTS else []
