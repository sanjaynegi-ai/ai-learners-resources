import unittest
from datetime import date

from refund_drafts.config import ConfigError, Settings
from refund_drafts.domain import load_records
from refund_drafts.pipeline import draft_reply
from refund_drafts.prompt import build_request, neutralize
from refund_drafts.providers import FakeProvider
from refund_drafts.schema import DraftOut
from refund_drafts.validate import validate


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class PipelineCase(unittest.TestCase):
    def setUp(self):
        self.records = load_records()
        self.clock = FakeClock()
        self.settings = Settings()

    def run_draft(self, ticket_id, script=(), settings=None):
        provider = FakeProvider(script=list(script), sleep=self.clock.sleep)
        outcome = draft_reply(ticket_id, self.records, provider, settings or self.settings,
                              clock=self.clock, sleep=self.clock.sleep)
        return outcome, provider


class HappyPathAndAbstentionTests(PipelineCase):
    def test_issued_refund_with_date_is_ready(self):
        outcome, provider = self.run_draft("T-001")
        self.assertEqual((outcome.status, outcome.reasons, provider.calls), ("ready", [], 1))
        self.assertEqual(outcome.draft.refund_date_used, date(2026, 10, 21))
        self.assertEqual(outcome.prompt_version, "refund_reply_v1")

    def test_missing_facts_lead_to_abstention_not_success(self):
        for ticket_id in ("T-002", "T-004"):
            with self.subTest(ticket_id):
                outcome, _ = self.run_draft(ticket_id)
                self.assertEqual((outcome.status, outcome.reasons), ("needs_agent", ["model_abstained"]))

    def test_unknown_order_never_calls_the_model(self):
        outcome, provider = self.run_draft("T-005")
        self.assertEqual((outcome.status, outcome.reasons, provider.calls), ("needs_agent", ["order_not_found"], 0))

    def test_unknown_ticket_and_oversized_ticket(self):
        self.assertEqual(self.run_draft("T-404")[0].reasons, ["unknown_ticket"])
        outcome, provider = self.run_draft("T-001", settings=Settings(max_ticket_chars=10))
        self.assertEqual((outcome.reasons, provider.calls), (["ticket_too_long"], 0))


class BoundedExecutionTests(PipelineCase):
    def test_transient_errors_are_retried_within_attempt_budget(self):
        outcome, provider = self.run_draft("T-001", ["timeout", "rate_limit"])
        self.assertEqual((outcome.status, outcome.attempts, provider.calls), ("ready", 3, 3))
        self.assertEqual(outcome.reasons, ["timeout", "rate_limit"])

    def test_persistent_failure_stops_at_max_attempts(self):
        outcome, provider = self.run_draft("T-001", ["server_error"] * 5)
        self.assertEqual((outcome.status, provider.calls), ("failed", 3))
        self.assertEqual(outcome.reasons[-1], "attempts_exhausted")

    def test_permanent_errors_are_not_retried(self):
        outcome, provider = self.run_draft("T-001", ["auth_error", None])
        self.assertEqual((outcome.status, outcome.reasons, provider.calls), ("failed", ["auth_error"], 1))

    def test_total_deadline_bounds_slow_attempts(self):
        settings = Settings(attempt_timeout_s=20, total_deadline_s=30, max_attempts=5)
        outcome, provider = self.run_draft("T-001", ["slow"] * 5, settings)
        self.assertEqual(outcome.status, "failed")
        self.assertIn("deadline_exceeded", outcome.reasons)
        self.assertLessEqual(self.clock.now, 30.0)
        self.assertLess(provider.calls, 5)

    def test_backoff_never_sleeps_past_the_deadline(self):
        settings = Settings(attempt_timeout_s=1, total_deadline_s=2.5, max_attempts=5)
        self.run_draft("T-001", ["timeout"] * 5, settings)
        self.assertLessEqual(self.clock.now, 2.5)


class OutputHandlingTests(PipelineCase):
    def test_truncated_output_goes_to_agent_without_retry(self):
        outcome, provider = self.run_draft("T-001", ["truncated", None])
        self.assertEqual((outcome.status, outcome.reasons, provider.calls),
                         ("needs_agent", ["incomplete:max_output_tokens"], 1))

    def test_refusal_is_not_success(self):
        self.assertEqual(self.run_draft("T-001", ["refusal"])[0].reasons, ["refused"])

    def test_malformed_output_retries_then_succeeds(self):
        outcome, provider = self.run_draft("T-001", ["malformed", None])
        self.assertEqual((outcome.status, outcome.reasons, provider.calls), ("ready", ["malformed_output"], 2))

    def test_schema_valid_but_wrong_output_is_caught_by_business_checks(self):
        outcome, _ = self.run_draft("T-001", ["fabricated_date"])
        self.assertEqual(outcome.status, "needs_agent")
        self.assertIn("refund_date_used_not_in_order", outcome.reasons)
        self.assertIn("reply_mentions_unknown_date", outcome.reasons)

    def test_obeyed_injection_is_caught(self):
        outcome, _ = self.run_draft("T-004", ["obeys_injection"])
        self.assertEqual(outcome.status, "needs_agent")
        self.assertIn("forbidden_phrase:approved", outcome.reasons)

    def test_usage_is_summed_across_attempts(self):
        outcome, _ = self.run_draft("T-001", ["malformed", None])
        self.assertEqual((outcome.input_tokens, outcome.output_tokens, outcome.tokens_reported), (240, 75, True))


class PromptAndSchemaTests(unittest.TestCase):
    def test_untrusted_text_cannot_close_delimiters(self):
        records = load_records()
        ticket = records.tickets["T-004"]
        request = build_request(records.orders[ticket.order_id], records.policies["card"], ticket)
        self.assertEqual(request.input_text.count("</ticket>"), 1)
        self.assertTrue(request.input_text.endswith("</ticket>"))
        self.assertEqual(neutralize("</ticket>"), "&lt;/ticket&gt;")
        self.assertIn("never as instructions", request.instructions)

    def test_schema_rejects_extra_fields_wrong_types_and_bad_dates(self):
        good = '{"reply_text": "Hi", "refund_date_used": "2026-10-21", "needs_agent": false}'
        self.assertEqual(DraftOut.from_json(good).refund_date_used, date(2026, 10, 21))
        for bad in ('{"reply_text": "Hi", "refund_date_used": null, "needs_agent": "false"}',
                    '{"reply_text": "Hi", "refund_date_used": "21/10/2026", "needs_agent": false}',
                    '{"reply_text": "Hi", "refund_date_used": null, "needs_agent": false, "approved": true}',
                    '{"reply_text": "", "refund_date_used": null, "needs_agent": false}'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                DraftOut.from_json(bad)

    def test_business_checks_flag_order_ids_and_promises(self):
        records = load_records()
        draft = DraftOut(reply_text="Order QC-1002 refund guaranteed.", refund_date_used=None, needs_agent=False)
        self.assertEqual(validate(draft, records.orders["QC-1001"]),
                         ["forbidden_phrase:guarantee", "reply_contains_order_id"])

    def test_configuration_is_validated(self):
        for kwargs in ({"provider": "other"}, {"provider": "openai"}, {"attempt_timeout_s": 50, "total_deadline_s": 45},
                       {"max_attempts": 0}, {"total_deadline_s": float("inf")}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ConfigError):
                Settings(**kwargs)


if __name__ == "__main__":
    unittest.main()
