"""Independent finite-burst model on the existing reliability lab's virtual clock.

Requires the full course checkout; never opens a socket. It deliberately models
only admission/queue/deadline for uniform work, not the HTTP cancellation phases.
"""
import argparse
import asyncio
from collections import Counter
import importlib.util
import json
from pathlib import Path


def predict(concurrency=2, queue_capacity=2):
    clock_path = Path(__file__).resolve().parents[3] / "llm/reliable-drafting/src/reliable_drafting/clock.py"
    if not clock_path.is_file():
        raise ValueError("Use full repository checkout for the simulator comparison")
    spec = importlib.util.spec_from_file_location("course_virtual_clock", clock_path)
    clock = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clock)

    async def burst():
        semaphore = asyncio.Semaphore(concurrency)
        in_system = 0
        async def one():
            nonlocal in_system
            if in_system >= concurrency + queue_capacity:
                return dict(status="rejected", queue_s=0, elapsed_s=0)
            in_system += 1
            started = asyncio.get_running_loop().time()
            waited = None
            try:
                async with asyncio.timeout(1):
                    async with semaphore:
                        waited = asyncio.get_running_loop().time() - started
                        await asyncio.sleep(.25)
                status = "completed"
            except TimeoutError:
                status = "timed_out"
            finally:
                in_system -= 1
            return dict(status=status, queue_s=waited, elapsed_s=asyncio.get_running_loop().time() - started)
        return await asyncio.gather(*(one() for _ in range(concurrency + queue_capacity + 4)))

    rows = clock.run_simulated(burst())
    return dict(kind="virtual-time simulation, not service observations", concurrency=concurrency,
                queue_capacity=queue_capacity, deadline_s=1, work_s=.25,
                simultaneous_arrivals=len(rows), outcomes=dict(Counter(r["status"] for r in rows)),
                samples=rows, assumptions="Uniform work, FIFO semaphore, no HTTP/scheduler/network overhead, no retries",
                clock="existing reliable-drafting/clock.py VirtualTimeLoop")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, choices=range(1, 5), default=2)
    parser.add_argument("--queue", type=int, choices=range(9), default=2)
    parser.add_argument("--output", type=Path, default=Path("results/load-prediction.json"))
    args = parser.parse_args()
    result = predict(args.concurrency, args.queue)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"kind": result["kind"], "outcomes": result["outcomes"]}))
