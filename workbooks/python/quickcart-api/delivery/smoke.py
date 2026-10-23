"""Bounded local HTTP contract checks. No model calls; synthetic identity only."""
import json
import sys
import urllib.error
import urllib.request


def request(base, path, expected, body=None, token=None):
    headers = {"Content-Type": "application/json", "Idempotency-Key": "delivery-0001"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(), headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=3)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        assert response.status == expected, (path, response.status, expected)
        return json.load(response)


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18000"
    assert base in ("http://127.0.0.1:18000", "http://127.0.0.1:8000"), "Local lab endpoints only"
    assert request(base, "/health", 200) == {"status": "ok"}
    body = {"ticket_id": "QC-811", "amount": 10, "tags": ["shipping"]}
    agent = "synthetic-token-merchant-a-agent"
    request(base, "/tickets", 401, body)
    # Allows rerunning against the same process: the same key/body returns 200.
    try:
        request(base, "/tickets", 201, body, agent)
    except AssertionError as error:
        if error.args[0] != ("/tickets", 200, 201):
            raise
    assert request(base, "/tickets", 200, body, agent)["amount"] == 10
    request(base, "/tickets/QC-811", 404, token="synthetic-token-merchant-b-agent")
    request(base, "/tickets", 422, {**body, "tenant": "merchant-b"}, agent)
    assert request(base, "/tickets/QC-811/triage", 200, {}, agent)["status"] == "triaged"
    print("PASS: health, authentication, idempotency, tenant isolation, schema and mock triage")


if __name__ == "__main__":
    main()
