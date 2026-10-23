import tempfile,unittest
from pathlib import Path
from review_service import ReviewStore

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'review.db';self.store=ReviewStore(self.path)
        self.payload={'event_id':'E1','ticket_id':'T1','text':'Synthetic refund inquiry'}
    def tearDown(self):self.store.db.close();self.temp.cleanup()
    def test_duplicate_and_persistence(self):
        self.assertEqual(self.store.accept('synthetic-lab-A',self.payload)[0],200)
        self.store.db.close();self.store=ReviewStore(self.path)
        self.assertTrue(self.store.accept('synthetic-lab-A',self.payload)[1]['duplicate'])
        self.assertEqual(self.store.snapshot()['review_count'],1)
    def test_auth_before_write(self):
        self.assertEqual(self.store.accept('wrong',self.payload)[0],403);self.assertEqual(self.store.snapshot()['review_count'],0)
    def test_body_and_identity_smuggling(self):
        for payload in ({**self.payload,'tenant':'B'},{**self.payload,'text':'x'*2001},{**self.payload,'event_id':True}):
            self.assertEqual(self.store.accept('synthetic-lab-A',payload)[0],400)
        self.assertEqual(self.store.snapshot()['review_count'],0)
    def test_key_payload_conflict(self):
        self.store.accept('synthetic-lab-A',self.payload)
        self.assertEqual(self.store.accept('synthetic-lab-A',{**self.payload,'text':'changed'})[0],409)
    def test_ambiguous_failure_retries_once_effect(self):
        payload={**self.payload,'event_id':'RETRY1'}
        self.assertEqual(self.store.accept('synthetic-lab-A',payload)[0],503)
        self.assertEqual(self.store.accept('synthetic-lab-A',payload)[0],200)
        self.assertEqual(self.store.snapshot()['review_count'],1)
