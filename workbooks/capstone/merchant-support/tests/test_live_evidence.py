import asyncio
import json
import unittest
from unittest.mock import patch

from merchant_support.core import OfflineProvider
from merchant_support.evaluate import evaluate
from merchant_support.provider import BedrockProvider


class LiveEvidence(unittest.IsolatedAsyncioTestCase):
    async def test_access_denial_stops_without_scoring_unexecuted_cases(self):
        class Denied(OfflineProvider):
            kind = "real-model-unreviewed"
            model = "never-contacted"
            last_error = None

            async def generate(self, evidence):
                self.last_error = "AccessDeniedException"
                raise RuntimeError("safe simulated rejection")

        report = await evaluate("cases.json", Denied(), "heldout")
        self.assertEqual(report["stopped_reason"], "AccessDeniedException")
        self.assertEqual(report["counts"]["scheduled_requests"], 8)
        self.assertEqual(report["counts"]["unexecuted"], 7)
        self.assertEqual(report["counts"]["provider_calls"], 1)
        self.assertEqual(report["control_gate"], "halt")
        self.assertIsNone(report["quality"])

    async def test_failed_child_does_not_reuse_prior_token_usage(self):
        class Child:
            returncode = 0

            async def communicate(self, payload):
                return json.dumps({"error": "AccessDeniedException"}).encode(), b""

        async def spawn(*args, **kwargs):
            return Child()

        provider = BedrockProvider("never-contacted")
        provider.last_usage = {"inputTokens": 100, "outputTokens": 40}
        with patch("merchant_support.provider.asyncio.create_subprocess_exec", spawn):
            with self.assertRaises(RuntimeError):
                await provider.generate([])
        self.assertIsNone(provider.last_usage)
        self.assertEqual(provider.last_error, "AccessDeniedException")


if __name__ == "__main__":
    unittest.main()
