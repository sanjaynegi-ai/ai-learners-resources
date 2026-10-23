"""Narrated walkthrough: untrusted proposals, trusted decisions, durable effects under failure.

    safe-actions              # runs every step against a fresh temporary database and fake services
"""
import tempfile
from pathlib import Path

from .boundaries import FakeProposalProvider, FakeService, call
from .executor import SimulatedCrash, approve, dispatch, propose_and_record
from .store import PRINCIPALS, Store


def step(title: str, outcome) -> None:
    print(f"- {title}\n    -> {outcome}")


def main() -> None:
    agent, lead, other_agent = PRINCIPALS["agent-a"], PRINCIPALS["lead-a"], PRINCIPALS["agent-b"]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "actions.sqlite3"
        store = Store(path)
        store.seed()
        print("Synthetic tenants, tickets and services. Effects are counted, never real.\n")
        print("1. Proposals from the model are validated, authorized and recorded")
        reply = call("send_customer_reply", {"ticket_id": "T-31", "body": "Sorry for the delay; an agent is on it."})
        cases = [
            ("normal reply", agent, "T-31", [reply]),
            ("same reply proposed again (new call_id)", agent, "T-31",
             [call("send_customer_reply", {"ticket_id": "T-31", "body": "Sorry for the delay; an agent is on it."})]),
            ("unknown tool", agent, "T-31", [call("delete_customer", {"ticket_id": "T-31"})]),
            ("arguments smuggle approval and tenant", agent, "T-31",
             [call("issue_goodwill_credit", {"order_id": "QC-3001", "amount_cents": 1500, "reason": "late",
                                             "approved_by": "lead-a", "tenant": "shop-b"})]),
            ("amount as a string", agent, "T-31",
             [call("issue_goodwill_credit", {"order_id": "QC-3001", "amount_cents": "1500", "reason": "late"})]),
            ("credit on another tenant's order", agent, "T-31",
             [call("issue_goodwill_credit", {"order_id": "QC-3002", "amount_cents": 1500, "reason": "late"})]),
            ("other tenant's agent acts on this ticket", other_agent, "T-31",
             [call("send_customer_reply", {"ticket_id": "T-31", "body": "Hello"})]),
            ("small credit, provider times out once", agent, "T-31",
             ["timeout", call("issue_goodwill_credit", {"order_id": "QC-3001", "amount_cents": 1500, "reason": "late"})]),
            ("large credit needs approval", agent, "T-31",
             [call("issue_goodwill_credit", {"order_id": "QC-3001", "amount_cents": 3000, "reason": "damaged"})]),
        ]
        decisions = {}
        for title, principal, ticket, script in cases:
            decision = propose_and_record(store, principal, ticket, FakeProposalProvider(list(script)))
            decisions[title] = decision
            step(f"{title} ({principal.user})", f"{decision.status} {decision.reasons or ''}".strip())

        print("\n2. Approval comes from trusted records, never from arguments")
        key = decisions["large credit needs approval"].action_key
        step("requester approves own credit", approve(store, agent, key))
        step("supervisor lead-a approves", approve(store, lead, key))

        print("\n3. Dispatch to external services under failure")
        email = FakeService("email", ["timeout_after"])           # Applied, but we never hear back
        credits = FakeService("credits", ["ok", "error"])          # Second credit fails once
        services = {"email": email, "credits": credits}
        step("first dispatch pass", dispatch(store, services))
        try:
            dispatch(store, services, crash_after_effect=True)
        except SimulatedCrash as crash:
            step("second pass crashes after an effect", crash)
        store.close()
        store = Store(path)                                         # Restart: only the database survives
        step("after restart, third pass", dispatch(store, services))
        step("fourth pass (nothing left)", dispatch(store, services))
        print(f"\nReal-world effects: {email.effects} email sent, {credits.effects} credits issued "
              f"(email service saw {email.calls} calls, credit service {credits.calls}).")
        recorded = dict(store.db.execute(
            "SELECT tool, COUNT(*) FROM actions WHERE status IN (\x27queued\x27, \x27done\x27) GROUP BY tool").fetchall())
        expected = (recorded.get("send_customer_reply", 0), recorded.get("issue_goodwill_credit", 0))
        if (email.effects, credits.effects) == expected and not store.queued():
            print("Every recorded action happened exactly once, despite a timeout after applying, an error and a crash.")
        else:
            print(f"MISMATCH: recorded actions expect {expected[0]} email(s) and {expected[1]} credit(s). "
                  "Something was duplicated or lost.")
        store.close()


if __name__ == "__main__":
    main()
