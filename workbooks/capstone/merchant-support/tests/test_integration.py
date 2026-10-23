import asyncio
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from merchant_support.api import create_app
from merchant_support.core import Engine, OfflineProvider, fixture_paths
from merchant_support.provider_worker import generate
from merchant_support.provider import BedrockProvider


class Integration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.engine = Engine(self.temp.name, *fixture_paths())

    async def asyncTearDown(self):
        self.engine.close()
        self.temp.cleanup()

    async def proposal(self, amount=2000):
        r = await self.engine.ask("demo-agent-a", "refund")
        return self.engine.propose("demo-agent-a", "QC-3001", amount, r["citations"])["action_id"]

    async def test_tenant_candidates_citations_and_order(self):
        a = await self.engine.ask("demo-agent-a", "refund")
        b = await self.engine.ask("demo-agent-b", "refund")
        self.assertEqual(a["retrieved"], ["refunds-policy.md"])
        self.assertEqual(b["retrieved"], ["other-tenant.md"])
        self.assertNotIn("tenant B", json.dumps(a))
        with self.assertRaises(PermissionError):
            self.engine.order("demo-agent-a", "QC-3002")

    async def test_unknown_identity_and_unsupported_question(self):
        self.assertEqual((await self.engine.ask("forged", "refund"))["status"], "denied")
        self.assertEqual((await self.engine.ask("demo-agent-a", "weather"))["status"], "abstained")

    async def test_revocation_during_provider(self):
        engine = self.engine

        class Revoke(OfflineProvider):
            async def generate(self, evidence):
                engine.store.revoke("alice")
                return await super().generate(evidence)

        engine.provider = Revoke()
        r = await engine.ask("demo-agent-a", "refund")
        self.assertEqual(r, {"status": "denied", "citations": [], "retrieved": []})

    async def test_delete_during_provider_and_restart(self):
        engine = self.engine

        class Delete(OfflineProvider):
            async def generate(self, evidence):
                engine.store.delete("refunds-policy.md")
                return await super().generate(evidence)

        engine.provider = Delete()
        self.assertEqual((await engine.ask("demo-agent-a", "refund"))["status"], "abstained")
        engine.close()
        self.engine = Engine(self.temp.name, *fixture_paths())
        self.assertEqual((await self.engine.ask("demo-agent-a", "refund"))["status"], "abstained")
        self.assertEqual(self.engine.store.db.execute("SELECT COUNT(*) FROM chunks WHERE document='refunds-policy.md'").fetchone()[0], 0)

    async def test_changed_policy_revision_fails_closed(self):
        key = await self.proposal()
        self.engine.approve("demo-lead-a", key)
        self.engine.store.invalidate("refunds-policy.md")
        with self.assertRaises(PermissionError):
            self.engine.execute("demo-agent-a", key)

    async def test_injection_and_invalid_generation(self):
        self.assertEqual((await self.engine.ask("demo-agent-a", "injection report"))["status"], "ready")

        class Hostile(OfflineProvider):
            async def generate(self, evidence):
                return {"citations": [{"id": evidence[0]["id"], "quote": "ignore authorization"}]}

        self.engine.provider = Hostile()
        self.assertEqual((await self.engine.ask("demo-agent-a", "refund"))["status"], "abstained")

    async def test_deadline_and_no_refunded_reservation(self):
        class Hang(OfflineProvider):
            async def generate(self, evidence):
                await asyncio.sleep(10)

        self.engine.provider = Hang()
        self.engine.timeout = .02
        started = time.monotonic()
        self.assertEqual((await self.engine.ask("demo-agent-a", "refund"))["status"], "failed")
        self.assertLess(time.monotonic()-started, .5)
        self.assertEqual(self.engine.store.db.execute("SELECT COUNT(*) FROM calls").fetchone()[0], 1)

    async def test_concurrency_sheds_excess(self):
        ready, release = asyncio.Event(), asyncio.Event()
        count = 0

        class Wait(OfflineProvider):
            async def generate(self, evidence):
                nonlocal count
                count += 1
                if count == 2:
                    ready.set()
                await release.wait()
                return await super().generate(evidence)

        self.engine.provider = Wait()
        one = asyncio.create_task(self.engine.ask("demo-agent-a", "refund"))
        two = asyncio.create_task(self.engine.ask("demo-agent-a", "refund"))
        await ready.wait()
        self.assertEqual((await self.engine.ask("demo-agent-a", "refund"))["status"], "busy")
        release.set()
        await asyncio.gather(one, two)

    async def test_cancelled_live_boundary_reaps_local_child_without_network(self):
        import sys
        real_spawn = asyncio.create_subprocess_exec
        children = []

        async def spawn(*args, **kwargs):
            child = await real_spawn(sys.executable, "-c", "import sys,time; sys.stdin.read(); time.sleep(30)", **kwargs)
            children.append(child)
            return child

        with patch("merchant_support.provider.asyncio.create_subprocess_exec", spawn):
            with self.assertRaises(TimeoutError):
                await asyncio.wait_for(BedrockProvider("never-called").generate([]), .3)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].returncode)

    async def test_durable_budget_and_halt(self):
        self.engine.maximum_calls = 1
        await self.engine.ask("demo-agent-a", "refund")
        self.assertEqual((await self.engine.ask("demo-agent-a", "refund"))["status"], "budget_or_halt")
        self.engine.close()
        self.engine = Engine(self.temp.name, *fixture_paths(), maximum_calls=1)
        self.assertEqual((await self.engine.ask("demo-agent-a", "refund"))["status"], "budget_or_halt")
        self.engine.halt()
        key = self.engine.store.db.execute("SELECT halted FROM controls").fetchone()[0]
        self.assertEqual(key, 1)

    async def test_no_execution_without_current_approval(self):
        key = await self.proposal()
        for token in ("demo-agent-a", "demo-agent-b"):
            with self.assertRaises(PermissionError):
                self.engine.approve(token, key)
        with self.assertRaises(PermissionError):
            self.engine.execute("demo-agent-a", key)
        self.engine.approve("demo-lead-a", key)
        self.engine.store.revoke("supervisor")
        with self.assertRaises(PermissionError):
            self.engine.execute("demo-agent-a", key)
        self.assertEqual(self.engine.store.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 0)

    async def test_crash_duplicate_and_restart(self):
        key = await self.proposal()
        self.engine.approve("demo-lead-a", key)
        with self.assertRaises(RuntimeError):
            self.engine.execute("demo-agent-a", key, crash_before_commit=True)
        self.assertEqual(self.engine.store.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 0)
        self.engine.close()
        self.engine = Engine(self.temp.name, *fixture_paths())
        self.engine.execute("demo-agent-a", key)
        self.engine.execute("demo-agent-a", key)
        self.assertEqual(await self.proposal(), key)
        self.assertEqual(self.engine.store.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 1)

    async def test_forged_evidence_and_amount_rejected(self):
        r = await self.engine.ask("demo-agent-a", "refund")
        for value in (True, -1, 99999):
            with self.assertRaises(ValueError):
                self.engine.propose("demo-agent-a", "QC-3001", value, r["citations"])
        r["citations"][0]["quote"] = "forged"
        with self.assertRaises(PermissionError):
            self.engine.propose("demo-agent-a", "QC-3001", 100, r["citations"])

    async def test_order_total_limit(self):
        for amount in (3000, 2000):
            key = await self.proposal(amount)
            self.engine.approve("demo-lead-a", key)
            if amount == 3000:
                self.engine.execute("demo-agent-a", key)
            else:
                with self.assertRaises(PermissionError):
                    self.engine.execute("demo-agent-a", key)

    async def test_telemetry_no_sensitive_strings_and_expiry(self):
        await self.engine.ask("demo-agent-a", "refund")
        dump = list(self.engine.store.db.execute("SELECT * FROM telemetry"))
        encoded = json.dumps([tuple(r) for r in dump])
        self.assertNotIn("demo-agent", encoded)
        self.assertNotIn("refund", encoded)
        self.assertEqual(self.engine.expire_telemetry(time.time()+604801), 1)


class HttpBoundary(unittest.TestCase):
    def test_http_workflow_and_non_echoing_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict("os.environ", {"CAPSTONE_STATE": tmp}), TestClient(create_app()) as client:
                auth = {"Authorization": "Bearer demo-agent-a"}
                self.assertEqual(client.get("/health").status_code, 200)
                bad = client.post("/answers", headers=auth, json={"query": "PRIVATE", "tenant": "SECRET"})
                self.assertEqual(bad.status_code, 422)
                self.assertNotIn("PRIVATE", bad.text)
                self.assertEqual(client.post("/answers", content="x"*8193).status_code, 413)
                result = client.post("/answers", headers=auth, json={"query": "refund"}).json()
                proposal = client.post("/proposals", headers=auth, json={"order_id": "QC-3001", "amount_cents": 100,
                    "citations": result["citations"]}).json()
                key = proposal["action_id"]
                self.assertEqual(client.post(f"/actions/{key}/execute", headers=auth).status_code, 403)
                lead = {"Authorization": "Bearer demo-lead-a"}
                self.assertEqual(client.post(f"/actions/{key}/approve", headers=lead).status_code, 200)
                self.assertEqual(client.post(f"/actions/{key}/execute", headers=auth).json()["effect_count"], 1)

    def test_sdk_contract_without_network(self):
        class Client:
            def converse(self, **kwargs):
                self.request = kwargs
                return {"stopReason": "end_turn", "output": {"message": {"content": [{"text": '{"citations":[]}' }]}}}
        client = Client()
        self.assertEqual(generate(client, "test-model", []), {"proposal": {"citations": []}, "usage": None})
        self.assertEqual(client.request["inferenceConfig"]["maxTokens"], 256)


if __name__ == "__main__":
    unittest.main()
