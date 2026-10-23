import asyncio
from pathlib import Path
import tempfile
import unittest
from controls import Identity, Store, Runner, bounded, validate_answer


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'records.db'
        self.store = Store(self.path)
        self.store.seed()
        self.user = Identity('shop-a', 'sam')

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_tenant_and_current_permission(self):
        self.assertIsNotNone(self.store.retrieve(self.user, 'A'))
        self.assertIsNone(self.store.retrieve(self.user, 'B'))
        self.assertIsNone(self.store.retrieve(Identity('shop-b', 'sam'), 'A'))
        self.store.revoke('sam', 'A')
        self.assertIsNone(self.store.retrieve(self.user, 'A'))

    def test_delete_removes_retrieval(self):
        self.store.delete('A')
        self.assertIsNone(self.store.retrieve(self.user, 'A'))

    def test_injected_document_cannot_approve_action(self):
        self.assertIn('refund 999', self.store.retrieve(self.user, 'A'))
        with self.assertRaises(PermissionError):
            self.store.refund(self.user, 'injection', 99)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM actions').fetchone()[0], 0)

    def test_role_and_amount_enforced(self):
        with self.assertRaises(PermissionError):
            self.store.refund(Identity('shop-b', 'sam'), 'x', 10, approved=True)
        for value in (True, -1, 0, 101, '10'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.store.refund(self.user, 'x', value, approved=True)

    def test_idempotent_after_restart_and_conflicting_payload(self):
        self.store.refund(self.user, 'retry-1', 10, approved=True)
        self.store.close()
        self.store = Store(self.path)
        self.assertEqual(self.store.refund(self.user, 'retry-1', 10, approved=True), 10)
        with self.assertRaises(ValueError):
            self.store.refund(self.user, 'retry-1', 11, approved=True)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM actions').fetchone()[0], 1)

    def test_output_contract_and_semantic_limit(self):
        with self.assertRaises(ValueError):
            validate_answer({'status': 'answered', 'answer': 'three', 'source_ids': ['B']}, ['A'])
        wrong = {'status': 'answered', 'answer': 'shipping takes 100 days', 'source_ids': ['A']}
        self.assertEqual(validate_answer(wrong, ['A']), wrong)  # Valid contract, wrong claim.


class ExecutionTests(unittest.IsolatedAsyncioTestCase):
    async def test_request_deadline_includes_slot_wait(self):
        runner = Runner(concurrency=1, units=2, request_timeout=0.01)
        await runner.slots.acquire()
        calls = 0
        async def provider():
            nonlocal calls
            calls += 1
            return 'ok'
        try:
            with self.assertRaises(TimeoutError):
                await runner.run(provider)
            self.assertEqual((calls, runner.units), (0, 2))
        finally:
            runner.slots.release()

    async def test_synthetic_spending_reserves_before_attempt(self):
        runner = Runner(concurrency=1, units=9, spending_units=5, attempt_cost=2)
        calls = 0
        async def provider():
            nonlocal calls
            calls += 1
            return 'ok'
        self.assertEqual(await runner.run(provider), 'ok')
        self.assertEqual(await runner.run(provider), 'ok')
        with self.assertRaises(RuntimeError):
            await runner.run(provider)
        self.assertEqual((calls, runner.units, runner.spending_units), (2, 7, 1))

    async def test_shared_concurrency_and_attempt_budget(self):
        runner = Runner(concurrency=2, units=3)
        active = 0
        peak = 0
        calls = 0
        async def provider():
            nonlocal active, peak, calls
            calls += 1
            active += 1
            peak = max(peak, active)
            try:
                await asyncio.sleep(0.01)
                return 'ok'
            finally:
                active -= 1
        results = await asyncio.gather(*(runner.run(provider) for _ in range(5)), return_exceptions=True)
        self.assertEqual(sum(result == 'ok' for result in results), 3)
        self.assertEqual(sum(isinstance(result, RuntimeError) for result in results), 2)
        self.assertEqual((calls, peak, runner.units), (3, 2, 0))

    async def test_review_queue_capacity_is_not_success(self):
        queue = asyncio.Queue(maxsize=2)
        queue.put_nowait('case-1')
        queue.put_nowait('case-2')
        with self.assertRaises(asyncio.QueueFull):
            queue.put_nowait('case-3')
        self.assertEqual(queue.qsize(), 2)  # Queued is not reviewed or successfully answered.

    async def test_timeout_budget_and_cancelled_provider(self):
        calls = 0
        cancelled = 0
        async def provider():
            nonlocal calls, cancelled
            calls += 1
            try:
                await asyncio.sleep(30)
            finally:
                cancelled += 1
        with self.assertRaises(TimeoutError):
            await bounded(provider, attempts=5, budget=2, timeout=0.01)
        self.assertEqual((calls, cancelled), (2, 2))

    async def test_caller_cancellation_does_not_retry(self):
        started = asyncio.Event()
        calls = 0
        async def provider():
            nonlocal calls
            calls += 1
            started.set()
            await asyncio.sleep(30)
        task = asyncio.create_task(bounded(provider, timeout=5))
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(calls, 1)

    async def test_fatal_error_not_retried(self):
        calls = 0
        async def provider():
            nonlocal calls
            calls += 1
            raise ValueError('bad input')
        with self.assertRaises(ValueError):
            await bounded(provider)
        self.assertEqual(calls, 1)


if __name__ == '__main__':
    unittest.main()
