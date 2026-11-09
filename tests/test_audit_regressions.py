"""Regression tests derived from the November 2026 source-code audit.

Tests use only disposable SQLite files and mocked network responses; no API fees.
"""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from factory_control.automation import AutomationEngine, Generation, SimulationProvider
from factory_control.cli import default_database_path
from factory_control.github_intake import get_approved_issues
from factory_control.providers import OpenAITextProvider, GeminiInteractionProvider
from factory_control.store import FactoryStore


class StubProvider:
    def __init__(self, *, simulated=False, fail_on=None):
        self.simulated = simulated
        self.fail_on = fail_on
        self.calls = 0

    def generate(self, role, instruction, objective, context):
        self.calls += 1
        if self.fail_on == self.calls:
            raise RuntimeError('confidential exception: should never be stored')
        return Generation(text=f'Draft {self.calls} for {role}', model='fake-model', simulated=self.simulated)


class EngineRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = FactoryStore(Path(self.tmp.name) / 'factory.sqlite')
        self.addCleanup(self.store.close)
        self.store.add_project('AUDIT-01', 'Audit fixture', 'operator')
        self.engine = AutomationEngine(self.store)

    def test_simulation_mislabelled_as_real_must_fail_closed(self):
        run = self.engine.create('AUDIT-01', 'Evaluate fake', provider='simulation')
        out = self.engine.run_one('simulation', StubProvider(simulated=False))
        self.assertEqual(out['state'], 'FAILED')
        self.assertEqual(out['current_step'], 0)
        self.assertNotEqual(out['state'], 'WAITING_APPROVAL')
        self.assertEqual(self.engine.get(run['id'])['outputs'], [])

    def test_real_run_cannot_mix_simulated_artifacts(self):
        run = self.engine.create('AUDIT-01', 'Evaluate', provider='openai')
        out = self.engine.run_one('openai', StubProvider(simulated=True))
        self.assertEqual(out['state'], 'FAILED')
        self.assertEqual(self.engine.get(run['id'])['outputs'], [])

    def test_tampered_previous_step_blocks_resume_before_external_call(self):
        run = self.engine.create('AUDIT-01', 'Sensitive input', provider='openai')
        self.assertEqual(self.engine.run_one('openai', StubProvider(fail_on=2))['state'], 'FAILED')
        with self.store.db:
            self.store.db.execute('UPDATE automation_outputs SET text=? WHERE run_id=? AND step_no=1',
                                  ('Modified unexpectedly', run['id']))
        self.engine.retry(run['id'])
        provider = StubProvider()
        self.assertEqual(self.engine.run_one('openai', provider)['error_code'], 'OUTPUT_INTEGRITY_FAILED')
        self.assertEqual(provider.calls, 0)

    def test_interrupted_run_recovery_requires_old_timestamp_and_is_manual(self):
        run = self.engine.create('AUDIT-01', 'Work', provider='simulation')
        self.engine.claim('simulation')
        with self.assertRaisesRegex(ValueError, 'còn mới'):
            self.engine.recover_stale(run['id'])
        with self.assertRaisesRegex(ValueError, 'ít nhất 300'):
            self.engine.recover_stale(run['id'], stale_seconds=2)
        old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(timespec='seconds')
        with self.store.db:
            self.store.db.execute('UPDATE automation_runs SET updated_at=? WHERE id=?', (old, run['id']))
        recovered = self.engine.recover_stale(run['id'])
        self.assertEqual(recovered['state'], 'FAILED')
        self.assertEqual(recovered['error_code'], 'INTERRUPTED_UNCERTAIN')
        self.assertEqual(len(self.engine.get(run['id'])['outputs']), 0)
        self.engine.retry(run['id'])
        self.assertEqual(self.engine.run_one('simulation', SimulationProvider())['state'], 'SIMULATED')
        self.assertTrue(any(e['action'] == 'AUTOMATION_RECOVERED_MANUALLY' for e in self.store.events('AUDIT-01')))

    def test_modified_evidence_size_rejected_even_if_hash_unchanged(self):
        proof = Path(self.tmp.name) / 'proof.txt'
        proof.write_text('safe test', encoding='utf-8')
        ev = self.store.add_evidence('AUDIT-01', 'PRODUCT_BRIEF', proof)
        with self.store.db:
            self.store.db.execute('UPDATE evidence SET byte_count=byte_count+1 WHERE id=?', (ev['id'],))
        self.assertFalse(self.store.verify_evidence(ev['id'])['valid'])


class MockHTTP:
    status = 200
    def __init__(self, payload, link=''):
        self.payload = payload
        self.headers = {'Link': link}
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self, n): return json.dumps(self.payload).encode('utf-8')


def issue(n):
    return {'number': n, 'title': f'Issue {n}', 'body': 'Review without secrets',
            'user': {'login': 'lengocsang-1991'}, 'labels': [{'name': 'factory:ready'}]}


class IntakeRegressionTests(unittest.TestCase):
    @patch('factory_control.github_intake.urllib.request.urlopen')
    def test_paginated_issues_are_not_silently_skipped(self, opener):
        opener.side_effect = [
            MockHTTP([issue(1)], '<https://api.github.com/a?page=2>; rel="next"'),
            MockHTTP([issue(2)]),
        ]
        rows = get_approved_issues('lengocsang-1991/ai-software-factory-control')
        self.assertEqual([r['number'] for r in rows], [1, 2])
        self.assertEqual(opener.call_count, 2)
        self.assertIn('page=2', opener.call_args.args[0].full_url)

    @patch('factory_control.github_intake.urllib.request.urlopen')
    def test_overflow_fails_loudly_instead_of_reporting_partial_results(self, opener):
        opener.side_effect = [MockHTTP([issue(i)], '<https://api.github.com/a?page=2>; rel="next"') for i in range(3)]
        with self.assertRaisesRegex(RuntimeError, 'GITHUB_TOO_MANY_ISSUES'):
            get_approved_issues('lengocsang-1991/ai-software-factory-control')

    @patch('factory_control.github_intake.urllib.request.urlopen')
    def test_unexpected_non_object_issues_are_ignored(self, opener):
        opener.return_value = MockHTTP([None, 1, 'text', issue(6), {'number': True, 'user': None}])
        rows = get_approved_issues('lengocsang-1991/ai-software-factory-control')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['number'], 6)


class ProviderRegressionTests(unittest.TestCase):
    @patch('factory_control.providers.urllib.request.urlopen')
    def test_incomplete_openai_response_rejected(self, opener):
        opener.return_value = MockHTTP({'status': 'incomplete', 'output': [{'content': [{'type': 'output_text', 'text': 'partial'}]}]})
        with self.assertRaisesRegex(RuntimeError, 'MODEL_INCOMPLETE'):
            OpenAITextProvider(model='gpt-test', api_key='dummy').generate('research', 'task', 'objective', '')

    @patch('factory_control.providers.urllib.request.urlopen')
    def test_openai_invalid_envelope_rejected(self, opener):
        opener.return_value = MockHTTP({'output': 'malformed'})
        with self.assertRaisesRegex(RuntimeError, 'MODEL_INVALID_RESPONSE'):
            OpenAITextProvider(model='gpt-test', api_key='dummy').generate('research', 'task', 'objective', '')

    @patch('factory_control.providers.urllib.request.urlopen')
    def test_incomplete_gemini_response_rejected(self, opener):
        opener.return_value = MockHTTP({'status': 'in_progress', 'steps': [{'type': 'model_output', 'content': [{'type':'text', 'text':'partial'}]}]})
        with self.assertRaisesRegex(RuntimeError, 'GEMINI_INCOMPLETE'):
            GeminiInteractionProvider(model='gemini-test', api_key='dummy').generate('research', 'task', 'objective', '')

    def test_model_ids_are_bounded(self):
        with self.assertRaisesRegex(ValueError, 'OPENAI_MODEL'):
            OpenAITextProvider(model='unsafe\nmodel', api_key='dummy')
        with self.assertRaisesRegex(ValueError, 'GEMINI_MODEL'):
            GeminiInteractionProvider(model='../../invalid', api_key='dummy')


class ConfigRegressionTests(unittest.TestCase):
    def test_explicit_db_location_does_not_depend_on_package_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'factory.sqlite'
            with patch.dict('os.environ', {'AI_FACTORY_DB': str(db)}):
                self.assertEqual(default_database_path(), db)


if __name__ == '__main__':
    unittest.main()
