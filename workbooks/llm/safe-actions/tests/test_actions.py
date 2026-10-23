import tempfile
import unittest
from pathlib import Path

from safe_actions.boundaries import FakeProposalProvider, FakeService, call
from safe_actions.executor import SimulatedCrash, approve, dispatch, idempotency_key, propose_and_record
from safe_actions.store import PRINCIPALS, Principal, Store

AGENT, LEAD, OTHER = PRINCIPALS["agent-a"], PRINCIPALS["lead-a"], PRINCIPALS["agent-b"]
REPLY = {"ticket_id": "T-31", "body": "An agent is on it."}
SMALL = {"order_id": "QC-3001", "amount_cents": 1500, "reason": "late"}
LARGE = {"order_id": "QC-3001", "amount_cents": 3000, "reason": "damaged"}


class StoreCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "actions.sqlite3"
        self.store = Store(self.path)
        self.store.seed()

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def propose(self, *script, principal=AGENT, ticket="T-31", **kwargs):
        return propose_and_record(self.store, principal, ticket, FakeProposalProvider(list(script)), **kwargs)

    def restart(self):
        self.store.close()
        self.store = Store(self.path)


class ProposalBoundaryTests(StoreCase):
    def test_valid_proposals_are_recorded_durably(self):
        decision = self.propose(call("send_customer_reply", REPLY))
        self.assertEqual(decision.status, "queued")
        self.restart()
        self.assertEqual(self.store.action(decision.action_key)["status"], "queued")

    def test_untrusted_arguments_are_rejected_before_anything_is_recorded(self):
        cases = {
            "unknown tool": (call("refund_everything", REPLY), ["unknown_tool"]),
            "not json": (call("send_customer_reply", "{ticket_id: T-31"), ["invalid_argument:json:json_invalid"]),
            "smuggled approval": (call("issue_goodwill_credit", {**SMALL, "approved_by": "lead-a"}),
                                  ["invalid_argument:approved_by:extra_forbidden"]),
            "string amount": (call("issue_goodwill_credit", {**SMALL, "amount_cents": "1500"}),
                              ["invalid_argument:amount_cents:int_type"]),
            "over hard limit": (call("issue_goodwill_credit", {**SMALL, "amount_cents": 99_900}),
                                ["invalid_argument:amount_cents:less_than_equal"]),
            "other tenant's order": (call("issue_goodwill_credit", {**SMALL, "order_id": "QC-3002"}), ["order_not_found"]),
            "more than the order": (call("issue_goodwill_credit", {**SMALL, "amount_cents": 4600}),
                                    ["amount_exceeds_order_total"]),
            "different ticket": (call("send_customer_reply", {**REPLY, "ticket_id": "T-32"}), ["ticket_mismatch"]),
        }
        for name, (proposal, reasons) in cases.items():
            with self.subTest(name):
                decision = self.propose(proposal)
                self.assertEqual((decision.status, decision.reasons), ("rejected", reasons))
        self.assertEqual(self.store.queued(), [])

    def test_tenant_and_role_come_from_the_principal(self):
        self.assertEqual(self.propose(call("send_customer_reply", REPLY), principal=OTHER).reasons, ["ticket_not_found"])
        viewer = Principal("viewer-a", "shop-a", "viewer")
        self.assertEqual(self.propose(call("send_customer_reply", REPLY), principal=viewer).reasons, ["role_not_allowed"])

    def test_provider_timeouts_are_bounded(self):
        self.assertEqual(self.propose("timeout", call("send_customer_reply", REPLY)).status, "queued")
        self.assertEqual(self.propose("timeout", "timeout").reasons, ["provider_timeout"])


class IdempotencyTests(StoreCase):
    def test_duplicate_proposals_with_new_call_ids_record_one_action(self):
        first = self.propose(call("issue_goodwill_credit", SMALL))
        second = self.propose(call("issue_goodwill_credit", SMALL))
        self.assertEqual((first.status, second.status, second.reasons), ("queued", "duplicate", ["already_queued"]))
        self.assertEqual(first.action_key, second.action_key)
        self.restart()
        self.assertEqual(self.propose(call("issue_goodwill_credit", SMALL)).status, "duplicate")

    def test_key_depends_on_content_not_on_order_of_fields(self):
        reordered = dict(reversed(list(SMALL.items())))
        self.assertEqual(idempotency_key("shop-a", "T-31", "issue_goodwill_credit", SMALL),
                         idempotency_key("shop-a", "T-31", "issue_goodwill_credit", reordered))
        self.assertNotEqual(idempotency_key("shop-a", "T-31", "issue_goodwill_credit", SMALL),
                            idempotency_key("shop-b", "T-31", "issue_goodwill_credit", SMALL))


class ApprovalTests(StoreCase):
    def test_large_credit_waits_for_a_different_supervisor_in_the_same_tenant(self):
        key = self.propose(call("issue_goodwill_credit", LARGE)).action_key
        credits = FakeService("credits")
        dispatch(self.store, {"credits": credits})
        self.assertEqual(credits.calls, 0)  # Pending actions are not in the outbox
        self.assertFalse(approve(self.store, AGENT, key))  # Agents cannot approve
        other_lead = Principal("lead-b", "shop-b", "supervisor")
        self.assertFalse(approve(self.store, other_lead, key))
        self_request = self.propose(call("issue_goodwill_credit", {**LARGE, "reason": "lead asks"}), principal=LEAD)
        self.assertFalse(approve(self.store, LEAD, self_request.action_key))  # No self-approval
        self.assertTrue(approve(self.store, LEAD, key))
        self.assertFalse(approve(self.store, LEAD, key))  # Already released
        dispatch(self.store, {"credits": credits})
        self.assertEqual((credits.effects, self.store.action(key)["status"]), (1, "done"))


class DispatchFaultTests(StoreCase):
    def queue_reply(self):
        return self.propose(call("send_customer_reply", REPLY)).action_key

    def test_timeout_after_apply_is_retried_with_the_same_key_and_applied_once(self):
        key = self.queue_reply()
        email = FakeService("email", ["timeout_after"])
        self.assertEqual(dispatch(self.store, {"email": email}).retry_later, 1)
        self.assertEqual(dispatch(self.store, {"email": email}).done, 1)
        self.assertEqual((email.calls, email.effects, self.store.action(key)["status"]), (2, 1, "done"))

    def test_timeout_before_apply_and_errors_retry_until_success(self):
        self.queue_reply()
        email = FakeService("email", ["timeout_before", "error"])
        for _ in range(3):
            dispatch(self.store, {"email": email})
        self.assertEqual((email.calls, email.effects), (3, 1))

    def test_persistent_failure_stops_and_asks_for_reconciliation(self):
        key = self.queue_reply()
        email = FakeService("email", ["error"] * 10)
        reports = [dispatch(self.store, {"email": email}) for _ in range(4)]
        self.assertEqual([r.failed for r in reports], [0, 0, 1, 0])
        self.assertEqual(self.store.action(key)["result"], "needs_reconciliation")
        self.assertEqual(email.calls, 3)

    def test_crash_after_effect_is_recovered_without_a_second_effect(self):
        key = self.queue_reply()
        email = FakeService("email")
        with self.assertRaises(SimulatedCrash):
            dispatch(self.store, {"email": email}, crash_after_effect=True)
        self.restart()
        self.assertEqual(self.store.action(key)["status"], "queued")
        self.assertEqual(dispatch(self.store, {"email": email}).done, 1)
        self.assertEqual((email.calls, email.effects), (2, 1))

    def test_internal_actions_complete_without_external_calls(self):
        key = self.propose(call("escalate_to_supervisor", {"ticket_id": "T-31", "note": "angry customer"})).action_key
        self.assertEqual(dispatch(self.store, {}).done, 1)
        self.assertEqual(self.store.action(key)["status"], "done")


if __name__ == "__main__":
    unittest.main()
