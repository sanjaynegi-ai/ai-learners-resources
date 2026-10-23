import math
from pathlib import Path
import tempfile
import unittest
from retrieval_lab.core import cosine, ingest, manifest, rank

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class RetrievalTests(unittest.TestCase):
    def test_repeatable_metadata_and_ids(self):
        one = ingest(FIXTURES)
        self.assertEqual(one, ingest(FIXTURES))
        self.assertEqual(len(one), 3)
        self.assertTrue(all(c.section and c.source_sha256 and c.start_word == 0 for c in one))

    def test_word_coverage_and_overlap(self):
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, 'a.md').write_text('# A\none two three four five six seven', encoding='utf-8')
            rows = ingest(temp, size=4, overlap=1)
            self.assertEqual([(r.start_word, r.end_word) for r in rows], [(0, 4), (3, 7)])
            self.assertEqual(rows[0].text.split()[-1], rows[1].text.split()[0])

    def test_source_or_configuration_changes_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp, 'a.md'); path.write_text('# A\none two three four', encoding='utf-8')
            old = ingest(temp, size=3, overlap=1)
            self.assertNotEqual(old[0].id, ingest(temp, size=4, overlap=1)[0].id)
            path.write_text('# A\none two three changed', encoding='utf-8')
            self.assertNotEqual(old[0].id, ingest(temp, size=3, overlap=1)[0].id)

    def test_parser_rejects_empty_and_unsupported(self):
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, 'bad.pdf').write_text('not actually PDF')
            with self.assertRaises(ValueError): ingest(temp)
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, 'empty.md').write_text('# Empty')
            with self.assertRaises(ValueError): ingest(temp)
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, 'punctuation.md').write_text('# Empty\n!!!')
            with self.assertRaises(ValueError): ingest(temp)

    def test_invalid_chunk_bounds(self):
        for size, overlap in ((0, 0), (4, 4), (4, -1), (True, 0)):
            with self.assertRaises(ValueError): ingest(FIXTURES, size=size, overlap=overlap)

    def test_paraphrase_is_authored_feature_not_learned(self):
        chunks = ingest(FIXTURES)
        self.assertEqual(rank(chunks, 'money back', mode='lexical'), [])
        self.assertTrue(rank(chunks, 'money back', mode='vector'))
        self.assertEqual(manifest(chunks, 40, 8)['toy_embedding'], 'authored-alias-counts-v1')

    def test_exact_identifier_and_unknown_query(self):
        chunks = ingest(FIXTURES)
        self.assertEqual(rank(chunks, 'DELAY-42')[0][0].document, 'shipping-tracking.md')
        for mode in ('lexical', 'vector', 'hybrid'):
            self.assertEqual(rank(chunks, 'zzzzunknown', mode=mode), [])

    def test_filter_before_ranking_and_hybrid_unique(self):
        chunks = ingest(FIXTURES)
        self.assertTrue(all(c.topic == 'refunds' for c, _ in rank(chunks, 'refund', topic='refunds')))
        self.assertEqual(rank(chunks, 'refund', topic='absent'), [])
        rows = rank(chunks, 'damaged refund', mode='hybrid')
        self.assertEqual(len(rows), len({c.id for c, _ in rows}))

    def test_cosine_dimensions_and_zero(self):
        self.assertAlmostEqual(cosine([1, 1], [1, 0]), 1 / math.sqrt(2))
        self.assertEqual(cosine([0, 0], [1, 0]), 0)
        for a, b in (([1], [1, 0]), ([], []), ([float('nan')], [1])):
            with self.assertRaises(ValueError): cosine(a, b)


if __name__ == '__main__':
    unittest.main()
