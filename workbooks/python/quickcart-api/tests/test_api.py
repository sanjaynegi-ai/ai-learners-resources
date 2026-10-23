import asyncio
import hashlib
import json
import unittest
from pathlib import Path

import httpx2
from fastapi.testclient import TestClient

from quickcart_api.app import create_app
from quickcart_api.config import ConfigError, Principal, Settings, load_principals

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
A_AGENT = "synthetic-token-merchant-a-agent"
A_SUPERVISOR = "synthetic-token-merchant-a-supervisor"
B_AGENT = "synthetic-token-merchant-b-agent"


def auth(token: str, key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if key is not None:
        headers["Idempotency-Key"] = key
    return headers


def settings(timeout: float = 0.5) -> Settings:
    return Settings(load_principals(FIXTURES / "synthetic-principals.json"), timeout)


class ApiCase(unittest.TestCase):
    provider = None
    timeout = 0.5

    def setUp(self) -> None:
        self.app = create_app(settings(self.timeout), self.provider)
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def create(self, body: dict, token: str = A_AGENT, key: str = "key-00000001"):
        return self.client.post("/tickets", json=body, headers=auth(token, key))


class HealthAndAuthTests(ApiCase):
    def test_health_needs_no_credentials(self):
        response = self.client.get("/health")
        self.assertEqual((response.status_code, response.json()), (200, {"status": "ok"}))

    def test_missing_and_unknown_tokens_are_401_with_challenge(self):
        for headers in ({}, auth("synthetic-token-unknown"), {"Authorization": "Basic abc"}):
            with self.subTest(headers=headers):
                response = self.client.get("/tickets/QC-1001", headers=headers)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.headers.get("www-authenticate"), "Bearer")


class ValidationTests(ApiCase):
    def test_valid_ticket_is_created(self):
        response = self.create({"ticket_id": "QC-1001", "amount": 25, "tags": ["refund"]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"ticket_id": "QC-1001", "amount": 25, "tags": ["refund"],
                                           "status": "open", "category": None})

    def test_strict_contract_rejects_coercion_and_unknown_fields(self):
        cases = {
            "bool amount": {"ticket_id": "QC-1001", "amount": True},
            "text amount": {"ticket_id": "QC-1001", "amount": "25"},
            "negative": {"ticket_id": "QC-1001", "amount": -1},
            "bad id": {"ticket_id": "1001", "amount": 1},
            "tenant smuggling": {"ticket_id": "QC-1001", "amount": 1, "tenant": "merchant-b"},
            "too many tags": {"ticket_id": "QC-1001", "amount": 1, "tags": [f"t{i}" for i in range(11)]},
            "tag format": {"ticket_id": "QC-1001", "amount": 1, "tags": ["Refund Now"]},
        }
        for name, body in cases.items():
            with self.subTest(name):
                self.assertEqual(self.create(body).status_code, 422)
        self.assertEqual(self.client.get("/tickets/QC-1001", headers=auth(A_AGENT)).status_code, 404)

    def test_validation_errors_do_not_echo_submitted_values(self):
        marker = "SYNTHETIC-PRIVATE-NOTE-7731"
        response = self.create({"ticket_id": "QC-1001", "amount": marker, "note": marker})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn(marker, response.text)
        locations = {tuple(item["loc"]) for item in response.json()["detail"]}
        self.assertEqual(locations, {("body", "amount"), ("body", "note")})

    def test_idempotency_key_is_required_and_bounded(self):
        body = {"ticket_id": "QC-1001", "amount": 1}
        self.assertEqual(self.client.post("/tickets", json=body, headers=auth(A_AGENT)).status_code, 422)
        self.assertEqual(self.create(body, key="short").status_code, 422)


class IdempotencyTests(ApiCase):
    body = {"ticket_id": "QC-1001", "amount": 25, "tags": ["refund"]}

    def test_replay_returns_original_without_second_ticket(self):
        first, second = self.create(self.body), self.create(self.body)
        self.assertEqual((first.status_code, second.status_code), (201, 200))
        self.assertEqual(first.json(), second.json())
        self.assertEqual(self.app.state.store.count("merchant-a"), 1)

    def test_same_key_different_body_and_same_id_different_key_conflict(self):
        self.create(self.body)
        changed = self.create({**self.body, "amount": 999})
        duplicate = self.create(self.body, key="key-00000002")
        self.assertEqual((changed.status_code, duplicate.status_code), (409, 409))
        self.assertEqual(self.client.get("/tickets/QC-1001", headers=auth(A_AGENT)).json()["amount"], 25)

    def test_concurrent_retries_create_exactly_one_ticket(self):
        async def burst():
            transport = httpx2.ASGITransport(app=self.app)
            async with httpx2.AsyncClient(transport=transport, base_url="http://test") as client:
                return await asyncio.gather(*(client.post("/tickets", json=self.body,
                                                          headers=auth(A_AGENT, "key-burst-01"))
                                              for _ in range(8)))
        statuses = sorted(response.status_code for response in asyncio.run(burst()))
        self.assertEqual(statuses, [200] * 7 + [201])
        self.assertEqual(self.app.state.store.count("merchant-a"), 1)


class TenantIsolationTests(ApiCase):
    def test_other_tenant_gets_404_and_ids_are_tenant_scoped(self):
        self.create({"ticket_id": "QC-1001", "amount": 25})
        self.assertEqual(self.client.get("/tickets/QC-1001", headers=auth(B_AGENT)).status_code, 404)
        self.assertEqual(self.client.post("/tickets/QC-1001/triage", headers=auth(B_AGENT)).status_code, 404)
        same_id = self.create({"ticket_id": "QC-1001", "amount": 7}, token=B_AGENT)
        self.assertEqual(same_id.status_code, 201)
        self.assertEqual(self.client.get("/tickets/QC-1001", headers=auth(A_AGENT)).json()["amount"], 25)

    def test_idempotency_keys_are_tenant_scoped(self):
        self.create({"ticket_id": "QC-1001", "amount": 25})
        other = self.create({"ticket_id": "QC-2001", "amount": 3}, token=B_AGENT)
        self.assertEqual(other.status_code, 201)


class CountingProvider:
    def __init__(self, result: object = "billing") -> None:
        self.calls, self.result = 0, result

    async def classify(self, ticket):
        self.calls += 1
        return self.result


class TriageTests(ApiCase):
    def setUp(self) -> None:
        self.provider = CountingProvider()
        super().setUp()
        self.create({"ticket_id": "QC-1001", "amount": 25, "tags": ["refund"]})

    def test_triage_records_category_and_does_not_repeat_provider_call(self):
        first = self.client.post("/tickets/QC-1001/triage", headers=auth(A_AGENT))
        second = self.client.post("/tickets/QC-1001/triage", headers=auth(A_AGENT))
        self.assertEqual(first.json()["category"], "billing")
        self.assertEqual((first.json()["status"], second.json(), self.provider.calls),
                         ("triaged", first.json(), 1))

    def test_unknown_or_foreign_ticket_never_reaches_provider(self):
        self.assertEqual(self.client.post("/tickets/QC-9999/triage", headers=auth(A_AGENT)).status_code, 404)
        self.assertEqual(self.client.post("/tickets/QC-1001/triage", headers=auth(B_AGENT)).status_code, 404)
        self.assertEqual(self.provider.calls, 0)

    def test_untrusted_provider_output_is_rejected(self):
        for result in ("refund everything", None, ["billing"], "BILLING"):
            with self.subTest(result=result):
                self.provider.result = result
                response = self.client.post("/tickets/QC-1001/triage", headers=auth(A_AGENT))
                self.assertEqual(response.status_code, 502)
                self.assertEqual(self.client.get("/tickets/QC-1001", headers=auth(A_AGENT)).json()["status"], "open")


class FailingProvider:
    async def classify(self, ticket):
        raise RuntimeError("synthetic provider outage with internal detail")


class StuckProvider:
    def __init__(self) -> None:
        self.cancelled = False

    async def classify(self, ticket):
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled = True


class ProviderFailureTests(ApiCase):
    timeout = 0.05

    def test_provider_error_is_502_without_internal_detail(self):
        self.app.state.provider = FailingProvider()
        self.create({"ticket_id": "QC-1001", "amount": 25})
        response = self.client.post("/tickets/QC-1001/triage", headers=auth(A_AGENT))
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("internal detail", response.text)

    def test_timeout_is_504_and_provider_call_is_cancelled(self):
        stuck = StuckProvider()
        self.app.state.provider = stuck
        self.create({"ticket_id": "QC-1001", "amount": 25})
        response = self.client.post("/tickets/QC-1001/triage", headers=auth(A_AGENT))
        self.assertEqual(response.status_code, 504)
        self.assertTrue(stuck.cancelled)


class ConfigTests(unittest.TestCase):
    def test_tokens_are_matched_by_hash_and_fixture_has_no_plaintext(self):
        loaded = settings()
        self.assertEqual(loaded.authenticate(A_SUPERVISOR), Principal("merchant-a", "supervisor"))
        self.assertIsNone(loaded.authenticate(hashlib.sha256(A_AGENT.encode()).hexdigest()))
        self.assertNotIn("synthetic-token", (FIXTURES / "synthetic-principals.json").read_text())

    def test_invalid_configuration_fails_at_startup(self):
        principals = load_principals(FIXTURES / "synthetic-principals.json")
        for timeout in (0, -1, 11, float("nan"), float("inf"), True):
            with self.subTest(timeout=timeout), self.assertRaises(ConfigError):
                Settings(principals, timeout)
        with self.assertRaises(ConfigError):
            Settings({}, 0.5)
        with self.assertRaises(ConfigError):
            load_principals(FIXTURES / "missing.json")

    def test_sample_fixture_tickets_are_valid_requests(self):
        app = create_app(settings())
        with TestClient(app) as client:
            for index, body in enumerate(json.loads((FIXTURES / "tickets.json").read_text())):
                response = client.post("/tickets", json=body, headers=auth(A_AGENT, f"fixture-key-{index:04d}"))
                self.assertEqual(response.status_code, 201, body["ticket_id"])


if __name__ == "__main__":
    unittest.main()
