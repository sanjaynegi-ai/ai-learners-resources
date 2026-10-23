"""Acceptance check for the independent DELETE exercise; run explicitly, not part of tests/.

From the quickcart-api directory:
    uv run python exercises/check_delete.py              # checks your route in src/quickcart_api/app.py
    uv run python exercises/check_delete.py --reference  # checks the inspectable reference router
"""
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from quickcart_api.app import create_app
from quickcart_api.config import Settings, load_principals

USE_REFERENCE = "--reference" in sys.argv
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def auth(token: str, key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer synthetic-token-{token}"}
    if key:
        headers["Idempotency-Key"] = key
    return headers


class DeleteRequirement(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app(Settings(load_principals(FIXTURES / "synthetic-principals.json")))
        if USE_REFERENCE:
            from delete_reference import router
            app.include_router(router)
        self.client = TestClient(app)
        self.body = {"ticket_id": "QC-1001", "amount": 25}
        created = self.client.post("/tickets", json=self.body, headers=auth("merchant-a-agent", "key-original"))
        self.assertEqual(created.status_code, 201)

    def delete(self, token: str, ticket_id: str = "QC-1001"):
        return self.client.delete(f"/tickets/{ticket_id}", headers=auth(token))

    def test_route_exists(self):
        self.assertNotIn(self.delete("merchant-a-supervisor").status_code, (404, 405),
                         "DELETE /tickets/{ticket_id} is not implemented yet")

    def test_supervisor_deletes_own_tenant_ticket(self):
        response = self.delete("merchant-a-supervisor")
        self.assertEqual((response.status_code, response.content), (204, b""))
        self.assertEqual(self.client.get("/tickets/QC-1001", headers=auth("merchant-a-agent")).status_code, 404)
        self.assertEqual(self.delete("merchant-a-supervisor").status_code, 404, "A repeated delete is 404")

    def test_agent_is_forbidden_whether_or_not_ticket_exists(self):
        self.assertEqual(self.delete("merchant-a-agent").status_code, 403)
        self.assertEqual(self.delete("merchant-a-agent", "QC-9999").status_code, 403)
        self.assertEqual(self.client.get("/tickets/QC-1001", headers=auth("merchant-a-agent")).status_code, 200)

    def test_other_tenant_and_anonymous_cannot_delete(self):
        self.assertIn(self.delete("merchant-b-agent").status_code, (403, 404))
        self.assertEqual(self.client.delete("/tickets/QC-1001").status_code, 401)
        self.assertEqual(self.client.get("/tickets/QC-1001", headers=auth("merchant-a-agent")).status_code, 200)

    def test_invalid_id_is_rejected_before_lookup(self):
        self.assertEqual(self.delete("merchant-a-supervisor", "not-a-ticket").status_code, 422)

    def test_replay_after_delete_conflicts_but_new_key_can_recreate(self):
        self.assertEqual(self.delete("merchant-a-supervisor").status_code, 204)
        replay = self.client.post("/tickets", json=self.body, headers=auth("merchant-a-agent", "key-original"))
        self.assertEqual(replay.status_code, 409, "Replaying the original key must not resurrect the ticket")
        fresh = self.client.post("/tickets", json=self.body, headers=auth("merchant-a-agent", "key-recreate"))
        self.assertEqual(fresh.status_code, 201)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]], verbosity=2)
