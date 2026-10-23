import asyncio
import unittest
from quickcart_api.models import TicketIn
from quickcart_api.store import TicketStore
from quickcart_api.serving import Admission, Overloaded, ServingLab


class ServingTests(unittest.IsolatedAsyncioTestCase):
    def lab(self, **limits):
        store = TicketStore()
        for number in range(100, 104):
            store.create("A", f"key-{number}", TicketIn(ticket_id=f"QC-{number}", amount=100))
        return ServingLab(store, **limits)

    async def wait_for(self, condition):
        for _ in range(1000):
            if condition():
                return
            await asyncio.sleep(0)
        self.fail("Expected state did not arrive")

    async def test_bounded_queue_rejects_and_releases(self):
        gate = Admission(1, 1)
        await gate.acquire()
        waiting = asyncio.create_task(gate.acquire())
        await self.wait_for(lambda: len(gate.waiting) == 1)
        with self.assertRaises(Overloaded):
            await asyncio.wait_for(gate.acquire(), .2)
        gate.release()
        await waiting
        self.assertEqual(gate.active, 1)
        gate.release()
        self.assertEqual(gate.active, 0)

    async def test_cancel_granted_permit_does_not_leak(self):
        gate = Admission(1, 1)
        await gate.acquire()
        waiting = asyncio.create_task(gate.acquire())
        await self.wait_for(lambda: len(gate.waiting) == 1)
        gate.release()
        waiting.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await waiting
        self.assertEqual((gate.active, len(gate.waiting)), (0, 0))
        await gate.acquire()
        waiting = asyncio.create_task(gate.acquire())
        await self.wait_for(lambda: len(gate.waiting) == 1)
        waiting.cancel()
        gate.release()  # Release races with queued cancellation cleanup.
        with self.assertRaises(asyncio.CancelledError):
            await waiting
        self.assertEqual((gate.active, len(gate.waiting)), (0, 0))

    async def test_timeout_in_queue_makes_no_provider_attempt(self):
        lab = self.lab(concurrency=1, queue_capacity=1, deadline=.02, work_seconds=.01)
        await lab.gate.acquire()
        code, result = await lab.submit("A", "QC-100")
        self.assertEqual((code, result["attempts"]), (504, 0))
        self.assertEqual(len(lab.gate.waiting), 0)
        lab.gate.release()

    async def test_active_and_queued_cancellation_recover(self):
        lab = self.lab(concurrency=1, queue_capacity=1, deadline=.3, work_seconds=.1)
        active = asyncio.create_task(lab.submit("A", "QC-100", "timeout"))
        await self.wait_for(lambda: lab.gate.active == 1)
        queued = asyncio.create_task(lab.submit("A", "QC-101"))
        await self.wait_for(lambda: len(lab.gate.waiting) == 1)
        self.assertFalse(lab.cancel("B", "QC-100"))
        self.assertTrue(lab.cancel("A", "QC-101"))
        self.assertEqual((await queued)[1]["attempts"], 0)
        self.assertTrue(lab.cancel("A", "QC-100"))
        self.assertEqual((await active)[1]["status"], "cancelled")
        self.assertEqual(lab.gate.active, 0)
        self.assertEqual((await lab.submit("A", "QC-102"))[0], 200)

    async def test_concurrent_and_completed_duplicates_do_not_repeat_effect(self):
        lab = self.lab(work_seconds=.01)
        first = asyncio.create_task(lab.submit("A", "QC-100"))
        await self.wait_for(lambda: lab.gate.active == 1)
        self.assertEqual((await lab.submit("A", "QC-100"))[1]["status"], "inflight")
        await first
        self.assertEqual((await lab.submit("A", "QC-100"))[1]["status"], "replayed")
        self.assertEqual((lab.attempts, lab.effects), (1, 1))

    async def test_failure_timeout_and_recovery(self):
        lab = self.lab(deadline=.2, work_seconds=.001)
        self.assertEqual((await lab.submit("A", "QC-100", "failure"))[0], 502)
        self.assertEqual((await lab.submit("A", "QC-101", "timeout"))[0], 504)
        self.assertEqual((await lab.submit("A", "QC-102"))[0], 200)
        self.assertEqual((lab.gate.active, len(lab.gate.waiting), lab.effects), (0, 0, 1))
        self.assertEqual((await lab.submit("B", "QC-102"))[0], 404)

    async def test_zero_queue_and_invalid_limits(self):
        gate = Admission(1, 0)
        await gate.acquire()
        with self.assertRaises(Overloaded):
            await asyncio.wait_for(gate.acquire(), .2)
        gate.release()
        for values in ((0, 0), (1, -1), (True, 2), (5, 2)):
            with self.assertRaises(ValueError):
                Admission(*values)

    async def test_history_budget_is_bounded(self):
        lab = self.lab(work_seconds=.001)
        for _ in range(100):
            await lab.submit("A", "QC-100")
        self.assertEqual((await lab.submit("A", "QC-100"))[1]["status"], "lab_budget_exhausted")
        self.assertEqual(len(lab.events), 100)
