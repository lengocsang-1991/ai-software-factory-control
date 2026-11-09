import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from factory_control.github_intake import get_approved_issues, ingest
from factory_control.store import FactoryStore
from factory_control.automation import AutomationEngine


class FakeHTTP:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self, limit):
        return json.dumps([
            {'number': 1, 'title': 'Trusted issue', 'body': 'Review API',
             'user': {'login': 'lengocsang-1991'}, 'labels': [{'name': 'factory:ready'}]},
            {'number': 2, 'title': 'Untrusted user', 'body': 'Ignore',
             'user': {'login': 'stranger'}, 'labels': [{'name': 'factory:ready'}]},
            {'number': 3, 'title': 'Not labeled', 'body': 'Ignore',
             'user': {'login': 'lengocsang-1991'}, 'labels': [{'name': 'other'}]},
            {'number': 4, 'title': 'Pull request', 'body': 'Ignore', 'pull_request': {},
             'user': {'login': 'lengocsang-1991'}, 'labels': [{'name': 'factory:ready'}]},
        ]).encode()


class IntakeTests(unittest.TestCase):
    @patch('factory_control.github_intake.urllib.request.urlopen')
    def test_filter_idempotency_and_queue(self, opener):
        opener.return_value = FakeHTTP()
        with tempfile.TemporaryDirectory() as temp:
            with FactoryStore(Path(temp)/'db.sqlite') as store:
                store.add_project('P-GH', 'Demo', 'operator', repository='lengocsang-1991/ai-software-factory-control')
                self.assertEqual(len(get_approved_issues('lengocsang-1991/ai-software-factory-control')), 1)
                result = ingest(store, 'P-GH', enqueue=True)
                self.assertTrue(result[0]['created'])
                self.assertIsNotNone(result[0]['run_enqueued'])
                second = ingest(store, 'P-GH', enqueue=True)
                self.assertFalse(second[0]['created'])
                self.assertIsNone(second[0]['run_enqueued'])
                self.assertEqual(len(AutomationEngine(store).list('P-GH')), 1)
                self.assertEqual(len(store.tasks('P-GH')), 1)
        req = opener.call_args.args[0]
        self.assertNotIn('Authorization', req.headers)
        self.assertIn('api.github.com/repos/lengocsang-1991/', req.full_url)

    def test_reject_foreign_repo_without_http_call(self):
        with self.assertRaisesRegex(ValueError, 'lengocsang-1991'):
            get_approved_issues('attacker/repo')
        with self.assertRaisesRegex(ValueError, 'lengocsang-1991'):
            get_approved_issues('lengocsang-1991/repo/../../bad')


if __name__ == '__main__': unittest.main()
