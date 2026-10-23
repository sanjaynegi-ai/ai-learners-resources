import tempfile
from pathlib import Path
import unittest
from approval_reference import authorize, dispatch_refund
from controls import Identity, Store


class ApprovalTests(unittest.TestCase):
    def test_distinct_threshold_and_revocation(self):
        self.assertTrue(authorize(50, ['sam'], {'sam', 'lee'}))
        self.assertTrue(authorize(60, ['sam', 'lee'], {'sam', 'lee'}))
        for approvers, current in ((['sam', 'sam'], {'sam', 'lee'}), (['sam', 'lee'], {'sam'})):
            with self.subTest(approvers=approvers), self.assertRaises(PermissionError):
                authorize(60, approvers, current)

    def test_invalid_policy_values(self):
        for value in (True, '60', 0, -1, 101):
            with self.subTest(value=value), self.assertRaises(ValueError):
                authorize(value, ['sam', 'lee'], {'sam', 'lee'})

    def test_tool_cannot_forge_approval_or_tenant(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Store(Path(temp) / 'ledger.db')
            try:
                user = Identity('shop-a', 'sam')
                for field in ('approved', 'tenant', 'subject'):
                    with self.subTest(field=field), self.assertRaises(PermissionError):
                        dispatch_refund(store, user, {'key': 'x', 'amount': 60, field: True}, ['sam', 'lee'], {'sam', 'lee'})
                with self.assertRaises(PermissionError):
                    dispatch_refund(store, user, {'key': 'x', 'amount': 60}, ['sam'], {'sam', 'lee'})
                self.assertEqual(store.db.execute('SELECT COUNT(*) FROM actions').fetchone()[0], 0)
                for _ in range(2):
                    dispatch_refund(store, user, {'key': 'x', 'amount': 60}, ['sam', 'lee'], {'sam', 'lee'})
                self.assertEqual(store.db.execute('SELECT COUNT(*) FROM actions').fetchone()[0], 1)
            finally:
                store.close()
