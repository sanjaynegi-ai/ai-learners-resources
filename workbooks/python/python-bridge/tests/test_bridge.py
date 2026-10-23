import asyncio
from dataclasses import FrozenInstanceError
import unittest
from quickcart_bridge.models import InputError, Ticket, parse_ticket, summarize
from quickcart_bridge.batch import collect


class ContractTests(unittest.TestCase):
    def test_normal_empty_and_duplicate_tags(self):
        ticket=parse_ticket({'ticket_id':'A','amount':10,'tags':['shipping','shipping']})
        self.assertEqual(summarize([ticket]),{'count':1,'total_units':10,'by_tag':{'shipping':1}})
        self.assertEqual(summarize([]),{'count':0,'total_units':0,'by_tag':{}})

    def test_invalid_external_values_and_unknown_fields(self):
        for payload in ({},[],{'ticket_id':'A','amount':True},{'ticket_id':'A','amount':-1},
                        {'ticket_id':'A','amount':'10'},{'ticket_id':'A','amount':1,'tags':'shipping'},
                        {'ticket_id':'A','amount':1,'approved':True}):
            with self.subTest(payload=payload), self.assertRaises(InputError): parse_ticket(payload)

    def test_constructor_and_mutability_boundary(self):
        with self.assertRaises(InputError): Ticket('A',True)
        with self.assertRaises(InputError): Ticket('A',1,(' ',))
        ticket=Ticket('A',1)
        with self.assertRaises(FrozenInstanceError): ticket.amount=2


class AsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_concurrency_result_order_and_no_input_mutation(self):
        tickets=[Ticket('A',1),Ticket('B',2),Ticket('C',3)]
        original=list(tickets); active=0; peak=0
        async def provider(ticket):
            nonlocal active,peak
            active+=1; peak=max(peak,active)
            try:
                await asyncio.sleep(0.01)
                return ticket.ticket_id
            finally: active-=1
        self.assertEqual(await collect(tickets,provider,concurrency=2),['A','B','C'])
        self.assertEqual((peak,active),(2,0)); self.assertEqual(tickets,original)

    async def test_deadline_cleans_children(self):
        active=0
        async def provider(ticket):
            nonlocal active
            active+=1
            try: await asyncio.sleep(30)
            finally: active-=1
        with self.assertRaises(TimeoutError):
            await collect([Ticket('A',1)],provider,deadline=0.01)
        self.assertEqual(active,0)

    async def test_caller_cancellation_propagates(self):
        started=asyncio.Event(); stopped=asyncio.Event()
        async def provider(ticket):
            started.set()
            try: await asyncio.sleep(30)
            finally: stopped.set()
        task=asyncio.create_task(collect([Ticket('A',1)],provider))
        await started.wait(); task.cancel()
        with self.assertRaises(asyncio.CancelledError): await task
        self.assertTrue(stopped.is_set())

    async def test_provider_failure_drains_other_tasks(self):
        active=0
        async def provider(ticket):
            nonlocal active
            active+=1
            try:
                if ticket.ticket_id=='A':
                    await asyncio.sleep(0.01)
                    raise RuntimeError('Synthetic failure')
                await asyncio.sleep(30)
                return ticket.ticket_id
            finally: active-=1
        with self.assertRaises(RuntimeError):
            await collect([Ticket('A',1),Ticket('B',2)],provider)
        self.assertEqual(active,0)

    async def test_bounds_and_provider_output(self):
        async def bad(ticket): return 1
        with self.assertRaises(TypeError): await collect([Ticket('A',1)],bad)
        for value in (True,0,11):
            with self.subTest(concurrency=value), self.assertRaises(ValueError):
                await collect([],bad,concurrency=value)
        with self.assertRaises(ValueError): await collect([Ticket(str(i),1) for i in range(21)],bad)
        for deadline in (True,0,-1,float('inf'),float('nan')):
            with self.subTest(deadline=deadline), self.assertRaises(ValueError):
                await collect([],bad,deadline=deadline)


if __name__=='__main__': unittest.main()
