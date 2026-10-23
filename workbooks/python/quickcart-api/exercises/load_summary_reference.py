"""Compare after independent attempt."""
import math


def summarize(samples):
    def p95(rows):
        values = sorted(r["client_ms"] for r in rows)
        return values[math.ceil(.95 * len(values)) - 1] if values else None
    statuses = [r["body"]["status"] for r in samples]
    useful = statuses.count("completed")
    return dict(requests=len(samples), useful=useful, rejected=statuses.count("rejected"),
                failed=sum(s in ("failed", "timed_out") for s in statuses),
                cancelled=statuses.count("cancelled"), replayed=statuses.count("replayed"),
                inflight=statuses.count("inflight"), useful_fraction=useful / len(samples) if samples else None,
                all_p95_ms=p95(samples), useful_p95_ms=p95([r for r in samples if r["body"]["status"] == "completed"]))
