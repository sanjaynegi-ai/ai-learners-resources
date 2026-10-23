import tempfile
import unittest
from langgraph.errors import GraphRecursionError
from approval_workflow.workflow import Application

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.app=Application(self.temp.name);self.app.seed()
    def tearDown(self):self.app.close();self.temp.cleanup()
    def test_restart_resume_once(self):
        self.app.start('R1');self.assertEqual(self.app.effects(),[])
        self.app.close();self.app=Application(self.temp.name)
        self.app.approve('R1','supervisor');self.assertEqual(self.app.resume('R1')['status'],'completed')
        self.app.resume('R1');self.assertEqual(len(self.app.effects()),1)
    def test_forged_resume_is_not_approval(self):
        self.app.start('R1');self.assertEqual(self.app.resume('R1',{'approved':True,'role':'supervisor'})['status'],'denied')
        self.assertEqual(self.app.effects(),[])
    def test_foreign_and_self_approval_denied(self):
        self.app.start('R1')
        for person in ('foreign','agent','missing'):
            with self.assertRaises(PermissionError): self.app.approve('R1',person)
    def test_revoked_approver_before_execution(self):
        self.app.start('R1');self.app.approve('R1','supervisor')
        with self.app.db:self.app.db.execute("UPDATE members SET active=0 WHERE id='supervisor'")
        self.app.seed();self.assertEqual(self.app.resume('R1')['status'],'denied');self.assertEqual(self.app.effects(),[])
    def test_denied_requester(self):
        with self.app.db:self.app.db.execute("UPDATE members SET active=0 WHERE id='agent'")
        self.assertEqual(self.app.start('R1')['status'],'denied');self.assertEqual(self.app.effects(),[])
    def test_crash_after_commit_replays_without_duplicate(self):
        self.app.start('R1');self.app.approve('R1','supervisor');self.app.crash_after_effect=True
        with self.assertRaises(RuntimeError):self.app.resume('R1')
        self.assertEqual(len(self.app.effects()),1)
        self.app.close();self.app=Application(self.temp.name)
        with self.app.db:self.app.db.execute("UPDATE members SET active=0 WHERE id='supervisor'")
        self.assertEqual(self.app.recover('R1')['status'],'completed');self.assertEqual(len(self.app.effects()),1)
    def test_invalid_state_and_amount(self):
        for amount in (True,0,1001):
            with self.assertRaises(ValueError):self.app.submit('R1',amount)
        with self.assertRaises(ValueError):self.app.validate({'request_id':'absent'})
        self.app.submit('R1')
        with self.assertRaises(ValueError):self.app.validate({'request_id':'R1','tenant':'B'})
        with self.assertRaises(ValueError):self.app.submit('R1',200)
    def test_bounded_transitions(self):
        with self.assertRaises(GraphRecursionError):self.app.start('R1',limit=1)
        self.assertEqual(self.app.effects(),[])
    def test_sequential_same_policy_without_checkpointer(self):
        self.app.submit('S1');self.app.approve('S1','supervisor')
        self.assertEqual(self.app.sequential('S1')['status'],'completed')
        self.app.sequential('S1');self.assertEqual(len(self.app.effects()),1)
    def test_explicit_rejection(self):
        self.app.start('R1');self.app.approve('R1','supervisor',False)
        self.assertEqual(self.app.resume('R1')['status'],'denied')
