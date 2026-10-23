"""Acceptance check for the daily credit cap; run explicitly, it is not part of tests/.

From the safe-actions directory:
    uv run python exercises/check_daily_cap.py              # checks your exercises/daily_cap.py
    uv run python exercises/check_daily_cap.py --reference  # checks the inspectable reference
"""
import sys
import tempfile
from pathlib import Path

from safe_actions.boundaries import FakeProposalProvider, call
from safe_actions.executor import propose_and_record
from safe_actions.store import PRINCIPALS, Store

if "--reference" in sys.argv:
    from daily_cap_reference import check_daily_cap
else:
    from daily_cap import check_daily_cap


def credit(amount, reason="late"):
    return call("issue_goodwill_credit", {"order_id": "QC-3001", "amount_cents": amount, "reason": reason})


with tempfile.TemporaryDirectory() as directory:
    store = Store(Path(directory) / "cap.sqlite3")
    try:
        store.seed()
        agent, other = PRINCIPALS["agent-a"], PRINCIPALS["agent-b"]

        def propose(principal, ticket, proposal):
            return propose_and_record(store, principal, ticket, FakeProposalProvider([proposal]), extra_checks=(check_daily_cap,))

        assert propose(agent, "T-31", credit(2000, "late")).status == "queued"
        assert propose(agent, "T-31", credit(3000, "damaged")).status == "pending_approval"  # Pending still counts
        replay = propose(agent, "T-31", credit(2000, "late"))
        assert replay.status == "duplicate", f"A replay must be a duplicate, not {replay.status} {replay.reasons}"
        assert propose(agent, "T-31", credit(1000, "goodwill")).status == "queued"            # 6000: exactly at cap
        over = propose(agent, "T-31", credit(1, "one more"))
        assert (over.status, over.reasons) == ("rejected", ["daily_cap_exceeded"]), (over.status, over.reasons)
        reply = propose(agent, "T-31", call("send_customer_reply", {"ticket_id": "T-31", "body": "Hi"}))
        assert reply.status == "queued", "Other tools are not capped"
        other_tenant = propose(other, "T-32", call("issue_goodwill_credit",
                                                   {"order_id": "QC-3002", "amount_cents": 5000, "reason": "late"}))
        assert other_tenant.status == "pending_approval", "The cap is per tenant"
    finally:
        store.close()  # Windows cannot delete an open database file

print(f"{check_daily_cap.__module__}: daily cap checks passed; explain your implementation independently.")
