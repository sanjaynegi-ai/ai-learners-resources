import unittest
from agents.exceptions import MaxTurnsExceeded,UserError,ModelBehaviorError
from tool_loop.demo import Principal,ScriptedModel,lookup,run

class LoopTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_runner_and_local_trace(self):
        result=await run();self.assertEqual(result['model_calls'],2)
        self.assertEqual(result['trusted_tool_entries'],[{'quantity':2}])
        self.assertIn('trace_end',result['local_trace_events'])
    async def test_denied_context_never_enters(self):
        p=Principal(role='viewer')
        with self.assertRaises(UserError):await run(p)
        self.assertEqual(p.entries,[])
    async def test_foreign_tenant_denied(self):
        with self.assertRaises(UserError):await run(Principal(tenant='B'))
    async def test_bad_arguments(self):
        for args in ('not-json','{"quantity":true}','{"quantity":6}'):
            p=Principal()
            with self.assertRaises((UserError,ModelBehaviorError)):await run(p,ScriptedModel(args))
            self.assertEqual(p.entries,[])
    async def test_turn_limit(self):
        p=Principal()
        with self.assertRaises(MaxTurnsExceeded):await run(p,ScriptedModel(loop=True),max_turns=2)
        self.assertLessEqual(len(p.entries),2)
    async def test_deadline(self):
        with self.assertRaises(TimeoutError):await run(model=ScriptedModel(hang=True),deadline=.02)
    async def test_tool_failure(self):
        with self.assertRaises(ValueError):lookup(Principal(),0)
