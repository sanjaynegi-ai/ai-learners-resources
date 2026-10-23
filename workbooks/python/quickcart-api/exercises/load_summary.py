"""Independent measurement report. Implement without importing the reference."""


def summarize(samples):
    """Return requests, useful, rejected, failed, cancelled, replayed, inflight,
    useful_fraction, all_p95_ms and useful_p95_ms from load_probe's sample list.

    'completed' is useful; failed includes failed/timed_out. Keep replayed and
    inflight separate from new useful work. Use nearest-rank p95 on client_ms,
    including every outcome in all_p95_ms. Empty denominator/family gives None.
    """
    raise NotImplementedError("Build denominators and latency distributions")
