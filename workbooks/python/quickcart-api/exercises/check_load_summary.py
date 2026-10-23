import argparse
import importlib


def check(module):
    summarize = importlib.import_module(module).summarize
    samples = [dict(client_ms=ms, body={"status": status}) for ms, status in (
        (100, "completed"), (200, "completed"), (5, "rejected"), (1000, "timed_out"),
        (30, "cancelled"), (10, "replayed"), (10, "inflight"), (500, "failed"))]
    assert summarize(samples) == dict(requests=8, useful=2, rejected=1, failed=2, cancelled=1,
                                      replayed=1, inflight=1, useful_fraction=.25,
                                      all_p95_ms=1000, useful_p95_ms=200)
    empty = summarize([])
    assert empty["requests"] == 0 and empty["useful_fraction"] is None and empty["all_p95_ms"] is None
    assert summarize(samples[2:])["useful_p95_ms"] is None
    print("Load-summary checks passed; measured independent analysis still required")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", action="store_true")
    args = parser.parse_args()
    check("load_summary_reference" if args.reference else "load_summary")
