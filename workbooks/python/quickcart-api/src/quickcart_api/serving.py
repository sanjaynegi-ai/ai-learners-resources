"""Single-event-loop bounded admission for the offline HTTP load lab only."""
import asyncio
import time
from collections import deque


class Overloaded(Exception):
    pass


class Admission:
    def __init__(self, concurrency=2, queue_capacity=2):
        if type(concurrency) is not int or not 1 <= concurrency <= 4:
            raise ValueError("concurrency must be 1..4")
        if type(queue_capacity) is not int or not 0 <= queue_capacity <= 8:
            raise ValueError("queue capacity must be 0..8")
        self.concurrency, self.queue_capacity = concurrency, queue_capacity
        self.active = self.max_active = self.max_waiting = 0
        self.waiting = deque()

    async def acquire(self):
        if self.active < self.concurrency:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            return
        if len(self.waiting) >= self.queue_capacity:
            raise Overloaded
        future = asyncio.get_running_loop().create_future()
        self.waiting.append(future)
        self.max_waiting = max(self.max_waiting, len(self.waiting))
        try:
            await future
        except BaseException:
            if future.done() and not future.cancelled():
                self.release()  # A granted permit was cancelled before acquire returned.
            else:
                try:
                    self.waiting.remove(future)
                except ValueError:
                    pass  # release already discarded this cancelled waiter.
            raise

    def release(self):
        while self.waiting:
            future = self.waiting.popleft()
            if not future.cancelled():
                future.set_result(True)  # Transfer the permit; active stays unchanged.
                return
        self.active -= 1


class ServingLab:
    def __init__(self, store, *, concurrency=2, queue_capacity=2, deadline=0.6, work_seconds=0.2):
        if not 0 < deadline <= 2 or not 0 < work_seconds <= 0.5:
            raise ValueError("Require deadline <=2 s and work <=0.5 s")
        self.store = store
        self.gate = Admission(concurrency, queue_capacity)
        self.deadline, self.work_seconds = deadline, work_seconds
        self.jobs = {}
        self.events = []  # Lab hard limit below bounds this synthetic-only history.
        self.attempts = self.effects = self.submissions = 0

    async def submit(self, tenant, ticket_id, scenario="normal"):
        started = time.perf_counter()
        key = (tenant, ticket_id)
        timing = {"queue_ms": 0.0, "attempts": 0, "effects": 0}
        ticket = self.store.get(*key)
        if ticket is None:
            return 404, {"status": "not_found"}
        if self.submissions >= 100:
            return 429, {"status": "lab_budget_exhausted"}
        self.submissions += 1
        if ticket.status == "triaged":
            status, code = "replayed", 200
        elif key in self.jobs:
            status, code = "inflight", 409
        else:
            task = asyncio.create_task(self._execute(key, scenario, timing))
            self.jobs[key] = task
            try:
                await task
                status, code = "completed", 200
            except Overloaded:
                status, code = "rejected", 429
            except TimeoutError:
                status, code = "timed_out", 504
            except asyncio.CancelledError:
                status, code = "cancelled", 409
            except RuntimeError:
                status, code = "failed", 502
            finally:
                self.jobs.pop(key, None)
        result = dict(status=status, **timing, server_ms=(time.perf_counter() - started) * 1000)
        self.events.append((tenant, result))
        return code, result

    async def _execute(self, key, scenario, timing):
        entered = time.perf_counter()
        acquired = False
        try:
            async with asyncio.timeout(self.deadline):
                await self.gate.acquire()
                acquired = True
                timing["queue_ms"] = (time.perf_counter() - entered) * 1000
                timing["attempts"] = 1
                self.attempts += 1
                await asyncio.sleep(self.work_seconds if scenario != "timeout" else self.deadline * 2)
                if scenario == "failure":
                    raise RuntimeError("Synthetic unavailable provider")
                if self.store.set_category(*key, "billing") is None:
                    raise RuntimeError("Ticket was removed")
                self.effects += 1
                timing["effects"] = 1
        finally:
            if acquired:
                self.gate.release()
            else:
                timing["queue_ms"] = (time.perf_counter() - entered) * 1000

    def cancel(self, tenant, ticket_id):
        task = self.jobs.get((tenant, ticket_id))
        return bool(task and task.cancel())

    def stats(self, tenant):
        events = [event for owner, event in self.events if owner == tenant]
        return dict(active=self.gate.active, waiting=len(self.gate.waiting),
                    max_active=self.gate.max_active, max_waiting=self.gate.max_waiting,
                    attempts=sum(e["attempts"] for e in events), effects=sum(e["effects"] for e in events),
                    events=events)
