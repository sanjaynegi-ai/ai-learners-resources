import json
from pathlib import Path
import tempfile
import unittest
from retrieval_lab.grounded import Store, answer, extractive_provider
from retrieval_lab.evaluation import comparison

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "security-metadata.json").read_text())


class GroundedTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.store.seed(ROOT / "secure-fixtures", META)

    def tearDown(self): self.store.close()

    def test_grounded_quote_has_version_and_hash(self):
        result = answer(self.store, 'alice', 'money back')
        self.assertEqual(result['status'], 'ready')
        citation = result['citations'][0]
        self.assertEqual(citation['quote'], META['documents'][citation['document']]['claim'])
        self.assertEqual(citation['revision'], 1)
        self.assertEqual(len(citation['source_sha256']), 64)

    def test_tenant_isolation_before_provider(self):
        seen = []
        def provider(evidence):
            seen.extend(e['document'] for e in evidence)
            return extractive_provider(evidence)
        answer(self.store, 'alice', 'refund', provider=provider)
        self.assertNotIn('other-tenant.md', seen)
        self.assertEqual(answer(self.store, 'bob', 'refund')['citations'][0]['document'], 'other-tenant.md')

    def test_role_and_unknown_session(self):
        self.assertEqual(answer(self.store, 'alice', 'private review')['citations'], [])
        self.assertEqual(answer(self.store, 'supervisor', 'private review')['status'], 'ready')
        self.assertEqual(answer(self.store, 'unknown', 'refund')['status'], 'denied')

    def test_revocation_before_provider_blocks_disclosure(self):
        def never(_): self.fail('Provider must not receive revoked evidence')
        result = answer(self.store, 'alice', 'refund', provider=never,
                        after_retrieval=lambda: self.store.change_acl('refunds-policy.md', ['supervisor']))
        self.assertEqual(result, {'status': 'abstained', 'citations': [], 'retrieved': []})

    def test_revocation_during_provider_blocks_response(self):
        def provider(evidence):
            self.store.revoke('alice')
            return extractive_provider(evidence)
        result = answer(self.store, 'alice', 'refund', provider=provider)
        self.assertEqual(result['status'], 'abstained')
        self.assertEqual(result['retrieved'], [])

    def test_stale_revision_and_expiration(self):
        self.store.invalidate('refunds-policy.md')
        self.assertEqual(answer(self.store, 'alice', 'refund')['status'], 'abstained')
        self.store.seed(ROOT / 'secure-fixtures', META)
        self.assertEqual(answer(self.store, 'alice', 'refund', now=1000)['status'], 'abstained')

    def test_delete_purges_payload_and_prevents_output(self):
        result = answer(self.store, 'alice', 'refund',
                        after_retrieval=lambda: self.store.delete('refunds-policy.md'))
        self.assertEqual(result['citations'], [])
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM chunks WHERE document='refunds-policy.md'").fetchone()[0], 0)
        row = self.store.db.execute("SELECT * FROM documents WHERE id='refunds-policy.md'").fetchone()
        self.assertEqual((row['claim'], row['value'], row['hash'], row['deleted']), ('', '', '', 1))
        self.assertEqual((row['tenant'], row['roles'], row['topic'], row['expires']), ('', '[]', '', 0))

    def test_unrelated_missing_and_conflicting(self):
        for query in ('holiday weather', 'refund amount'):
            self.assertEqual(answer(self.store, 'alice', query)['status'], 'abstained')
        self.assertEqual(answer(self.store, 'alice', 'conflict window')['status'], 'conflict')

    def test_injection_cannot_change_claim_or_citation(self):
        self.assertEqual(answer(self.store, 'alice', 'injection report')['citations'][0]['quote'],
                         'Injection reports require human review.')
        for proposal in ({'citations': [{'id': 'forged', 'quote': 'invented'}]},
                         {'citations': [], 'tenant': 'B'}):
            self.assertEqual(answer(self.store, 'alice', 'refund', provider=lambda _, p=proposal: p)['status'], 'abstained')
        invented = lambda evidence: {'citations': [{'id': evidence[0]['id'], 'quote': 'invented claim'}]}
        self.assertEqual(answer(self.store, 'alice', 'refund', provider=invented)['status'], 'abstained')

    def test_query_bound(self):
        for query in ('', 'x'*501, None):
            with self.assertRaises(ValueError): answer(self.store, 'alice', query)

    def test_deletion_persists_across_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'index.db'
            store = Store(path)
            store.seed(ROOT / 'secure-fixtures', META)
            store.delete('refunds-policy.md'); store.close()
            store = Store(path)
            try: self.assertEqual(answer(store, 'alice', 'refund')['status'], 'abstained')
            finally: store.close()

    def test_separate_evaluation_and_justified_change(self):
        report = comparison(ROOT)
        self.assertEqual(report['decision'], 'KEEP_HYBRID_FOR_THIS_FIXTURE_ONLY')
        hybrid = report['reports']['hybrid']
        self.assertEqual(hybrid['answers']['correct_outcomes'], hybrid['answers']['cases'])
        self.assertEqual(hybrid['retrieval']['forbidden_retrieval_count'], 0)
        self.assertGreater(hybrid['retrieval']['recall_at_3'], report['reports']['lexical']['retrieval']['recall_at_3'])
        injected = next(c for c in hybrid['cases'] if c['id'] == 'injection-output')
        self.assertEqual((injected['retrieval_hits'], injected['status']), (1, 'abstained'))
