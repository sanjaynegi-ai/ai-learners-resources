"""Actual HTTP boundary smoke. Only against a caller-selected local loopback server."""
import argparse
import json
import urllib.error
import urllib.request


def smoke(port):
    def call(path, token=None, body=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
            data=json.dumps(body).encode() if body is not None else None, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=4) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)
    assert call("/health")[0] == 200
    status, answer = call("/answers", "demo-agent-a", {"query": "refund"})
    assert status == 200 and answer["status"] == "ready"
    assert answer["retrieved"] == ["refunds-policy.md"]
    assert call("/orders/QC-3002", "demo-agent-a")[0] == 403
    status, proposal = call("/proposals", "demo-agent-a", {"order_id": "QC-3001",
        "amount_cents": 100, "citations": answer["citations"]})
    assert status == 200
    key = proposal["action_id"]
    # Repeat smoke may find an already approved/done action; no new effect is allowed.
    if proposal["status"] == "pending":
        denied, _ = call(f"/actions/{key}/execute", "demo-agent-a", {})
        if denied == 403:
            assert call(f"/actions/{key}/approve", "demo-lead-a", {})[0] == 200
    assert call(f"/actions/{key}/execute", "demo-agent-a", {})[1] == {"status": "done", "effect_count": 1}
    assert call(f"/actions/{key}/execute", "demo-agent-a", {})[1]["effect_count"] == 1
    return {"health": "pass", "tenant_denial": "pass", "answer": "pass", "action_id": key,
            "duplicate": "same durable effect", "kind": "local-http-synthetic"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=8013)
    args = p.parse_args()
    print(json.dumps(smoke(args.port), indent=2))
