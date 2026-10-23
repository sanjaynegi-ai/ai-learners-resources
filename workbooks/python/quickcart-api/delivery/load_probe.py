"""Bounded real TCP/HTTP observations against a server this runner owns on loopback.

No URL argument, remote target, provider call or automatic retry exists.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import platform
import socket
import threading
import time
import urllib.error
import urllib.request

import fastapi
import uvicorn
from quickcart_api.config import Settings, load_principals
from quickcart_api.load_app import create_load_app

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "synthetic-token-merchant-a-agent"


def nearest_p95(values):
    return sorted(values)[math.ceil(.95 * len(values)) - 1] if values else None


def observe(concurrency=2, queue_capacity=2):
    app = create_load_app(Settings(load_principals(ROOT / "fixtures/synthetic-principals.json")),
                          concurrency=concurrency, queue_capacity=queue_capacity,
                          deadline=1.0, work_seconds=0.25)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    base = f"http://127.0.0.1:{sock.getsockname()[1]}"
    server = uvicorn.Server(uvicorn.Config(app, access_log=False, log_level="error",
                                          timeout_graceful_shutdown=3))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    control_requests = 0
    request_lock = threading.Lock()
    samples = []

    def request(path, body=None, token=TOKEN):
        nonlocal control_requests
        with request_lock:
            control_requests += 1
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}",
                   "Idempotency-Key": "load-" + path.split("/")[-1]}
        # Creation keys use ticket identity, avoiding conflicts between distinct tickets.
        if path == "/tickets":
            headers["Idempotency-Key"] = "load-" + body["ticket_id"]
        req = urllib.request.Request(base + path, headers=headers,
                                     data=None if body is None else json.dumps(body).encode())
        started = time.perf_counter()
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            response = opener.open(req, timeout=3)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return dict(http=response.status, body=json.load(response),
                        retry_after=response.headers.get("Retry-After"),
                        client_start_s=started, client_end_s=time.perf_counter(),
                        client_ms=(time.perf_counter() - started) * 1000)

    def create(number):
        result = request("/tickets", dict(ticket_id=f"QC-{number}", amount=100, tags=["refund"]))
        assert result["http"] == 201, result

    def job(number, scenario="normal"):
        return request(f"/lab/tickets/QC-{number}/triage", scenario)

    def wait_for(predicate):
        end = time.monotonic() + 3
        for _ in range(60):
            if time.monotonic() >= end:
                break
            stats = request("/lab/stats")["body"]
            if predicate(stats):
                return stats
            time.sleep(.01)
        raise AssertionError("Phase coordination did not reach expected state")

    started = time.perf_counter()
    try:
        until = time.monotonic() + 5
        while not server.started and thread.is_alive() and time.monotonic() < until:
            time.sleep(.01)
        assert server.started, "Local server did not start"
        with ThreadPoolExecutor(max_workers=16) as pool:
            # Arrival is one synchronized finite burst, not a sustained request rate.
            for phase, first, count in (("baseline", 100, concurrency),
                                        ("overload", 200, concurrency + queue_capacity + 4)):
                for number in range(first, first + count):
                    create(number)
                barrier = threading.Barrier(count)
                def burst(number):
                    barrier.wait(timeout=3)
                    return job(number)
                futures = [pool.submit(burst, n) for n in range(first, first + count)]
                samples.extend(dict(phase=phase, **f.result(timeout=4)) for f in futures)

            create(300)
            pending = pool.submit(job, 300, "timeout")
            wait_for(lambda s: s["active"] == 1)
            samples.append(dict(phase="duplicate", **job(300)))
            denied_cancel = request("/lab/tickets/QC-300/cancel", {}, "synthetic-token-merchant-b-agent")
            assert not denied_cancel["body"]["cancel_requested"]
            assert request("/lab/tickets/QC-300/cancel", {})["body"]["cancel_requested"]
            samples.append(dict(phase="active_cancel", **pending.result(timeout=3)))

            if queue_capacity:
                holders = []
                for n in range(400, 400 + concurrency):
                    create(n)
                    holders.append(pool.submit(job, n, "timeout"))
                wait_for(lambda s: s["active"] == concurrency)
                create(450)
                queued = pool.submit(job, 450)
                wait_for(lambda s: s["waiting"] == 1)
                assert request("/lab/tickets/QC-450/cancel", {})["body"]["cancel_requested"]
                samples.append(dict(phase="queue_cancel", **queued.result(timeout=3)))
                for n in range(400, 400 + concurrency):
                    request(f"/lab/tickets/QC-{n}/cancel", {})
                samples.extend(dict(phase="active_cancel", **f.result(timeout=3)) for f in holders)

            for n, scenario in ((500, "failure"), (501, "timeout")):
                create(n)
                samples.append(dict(phase=scenario, **job(n, scenario)))
            for n in (600, 601):
                create(n)
                samples.append(dict(phase="recovery", **job(n)))
            samples.append(dict(phase="replay", **job(600)))
        stats = request("/lab/stats")["body"]
        assert stats["active"] == stats["waiting"] == 0
        assert stats["max_active"] <= concurrency and stats["max_waiting"] <= queue_capacity
        assert stats["attempts"] == sum(s["body"]["attempts"] for s in samples)
        assert stats["effects"] == sum(s["body"]["status"] == "completed" for s in samples)
        assert any(s["body"]["status"] == "rejected" and s["retry_after"] == "1" for s in samples)
        assert all(s["body"]["status"] == "completed" for s in samples if s["phase"] == "recovery")
        phases = {}
        for phase in sorted({s["phase"] for s in samples}):
            rows = [s for s in samples if s["phase"] == phase]
            phases[phase] = dict(requests=len(rows), outcomes=dict(Counter(s["body"]["status"] for s in rows)),
                                 client_p95_ms=nearest_p95([s["client_ms"] for s in rows]),
                                 queue_p95_ms=nearest_p95([s["body"]["queue_ms"] for s in rows]),
                                 arrival_span_ms=1000 * (max(s["client_start_s"] for s in rows) - min(s["client_start_s"] for s in rows)),
                                 observed_requests_per_s=len(rows) / (max(s["client_end_s"] for s in rows) - min(s["client_start_s"] for s in rows)))
        counts = Counter(s["body"]["status"] for s in samples)
        report = dict(environment=dict(python=platform.python_version(), os=platform.platform(),
                                       fastapi=fastapi.__version__, uvicorn=uvicorn.__version__,
                                       transport="real loopback TCP HTTP/1.1; one uvicorn event loop in owned thread"),
                      workload=dict(concurrency=concurrency, queue_capacity=queue_capacity, deadline_s=1,
                                    mock_work_s=.25, burst_requests=concurrency + queue_capacity + 4,
                                    client_threads_max=16, client_timeout_s=3, automatic_retries=0,
                                    duration_s=time.perf_counter() - started, measured_job_requests=len(samples),
                                    all_http_requests=control_requests, request_body_bound="synthetic ticket schema; enum scenario"),
                      prediction=dict(kind="ideal simultaneous-burst model, not service measurement",
                                      admitted=concurrency + queue_capacity, rejected=4,
                                      ideal_service_rate_per_s=concurrency / .25,
                                      caveat="Scheduling and queue deadline may change observed counts; no sustained-rate claim"),
                      totals=dict(requests=len(samples), outcomes=dict(counts),
                                  useful_completion_fraction=counts["completed"] / len(samples),
                                  all_client_p95_ms=nearest_p95([s["client_ms"] for s in samples]),
                                  completed_client_p95_ms=nearest_p95([s["client_ms"] for s in samples if s["body"]["status"] == "completed"]),
                                  failed_client_p95_ms=nearest_p95([s["client_ms"] for s in samples if s["body"]["status"] in ("failed", "timed_out")])),
                      phases=phases, stats=stats, samples=samples,
                      limits=["Mock work and local in-memory effects; no model quality or external-effect guarantee",
                              "Explicit cancellation endpoint exercised; client disconnect detection not implemented",
                              "Admission applies only to lab triage routes, not base API, TCP backlog or arbitrary clients",
                              "Single process; ticket state/idempotency do not survive restart; not a cloud/container benchmark"])
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()
        if thread.is_alive():
            raise RuntimeError("Owned server failed to stop")
    report["cleanup"] = "server thread stopped and listening socket closed"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, choices=range(1, 5), default=2)
    parser.add_argument("--queue", type=int, choices=range(9), default=2)
    parser.add_argument("--output", type=Path, default=Path("results/load.json"))
    args = parser.parse_args()
    report = observe(args.concurrency, args.queue)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phases": report["phases"], "cleanup": report["cleanup"]}))
