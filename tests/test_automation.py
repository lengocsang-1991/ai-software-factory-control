"""Behavioral tests of durable automation, explicit simulation and approval gates."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from factory_control.automation import AutomationEngine, Generation, RECIPES, SimulationProvider
from factory_control.store import FactoryStore


class FakeProvider:
    def __init__(self, fail_step=None):
        self.calls = []
        self.fail_step = fail_step

    def generate(self, role, instruction, objective, context):
        self.calls.append((role, context))
        if self.fail_step == len(self.calls):
            raise RuntimeError('failure with credential=SECRET_PLACEHOLDER')
        return Generation(text=f'Artifact {role}, no claim of verification', model='fake-test', simulated=False)


class AutomationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'db.sqlite'
        self.store = FactoryStore(self.path)
        self.addCleanup(self.store.close)
        self.store.add_project('P-TEST', 'Fixture', 'operator')
        self.engine = AutomationEngine(self.store)

    def test_all_sixteen_roles_have_full_review_recipe(self):
        self.assertEqual(len(RECIPES['full-review']), 16)
        self.assertEqual(len(set(RECIPES['full-review'])), 16)

    def test_simulation_stays_simulated_and_cannot_approve(self):
        run = self.engine.create('P-TEST', 'Demo objective')
        self.assertEqual(run['state'], 'QUEUED')
        r = self.engine.run_one('simulation', SimulationProvider())
        self.assertEqual(r['state'], 'SIMULATED')
        self.assertEqual(len(self.engine.get(run['id'])['outputs']), len(RECIPES['discovery']))
        with self.assertRaisesRegex(ValueError, 'Chỉ phê duyệt'):
            self.engine.decide(run['id'], 'APPROVED', 'operator')

    def test_real_provider_stub_requires_approval_then_approves(self):
        run = self.engine.create('P-TEST', 'Build an app', provider='openai')
        fake = FakeProvider()
        self.assertEqual(self.engine.run_one('openai', fake)['state'], 'WAITING_APPROVAL')
        self.assertEqual(len(fake.calls), len(RECIPES['discovery']))
        self.assertEqual(self.engine.get(run['id'])['current_step'], len(RECIPES['discovery']))
        outputs = self.engine.get(run['id'])['outputs']
        self.assertIn('Artifact', fake.calls[1][1])
        self.assertTrue(all(hashlib.sha256(o['text'].encode()).hexdigest() == o['sha256'] for o in outputs))
        self.assertEqual(self.engine.decide(run['id'], 'APPROVED', 'operator')['state'], 'APPROVED')
        self.assertIsNone(self.engine.run_one('openai', fake))
        with self.assertRaisesRegex(ValueError, 'Chỉ phê duyệt'):
            self.engine.decide(run['id'], 'APPROVED', 'operator')
        self.assertEqual(self.store.project('P-TEST')['stage'], 1)  # approval does not bypass quality gate

    def test_provider_failure_is_recorded_without_secret_leak_and_retry(self):
        run = self.engine.create('P-TEST', 'Run check', provider='openai')
        bad = FakeProvider(fail_step=2)
        self.assertEqual(self.engine.run_one('openai', bad)['state'], 'FAILED')
        saved = self.engine.get(run['id'])
        self.assertEqual(saved['current_step'], 1)
        self.assertNotIn('SECRET_PLACEHOLDER', str(saved))
        self.engine.retry(run['id'])
        new = FakeProvider()
        self.assertEqual(self.engine.run_one('openai', new)['state'], 'WAITING_APPROVAL')
        self.assertEqual(len(new.calls), len(RECIPES['discovery']) - 1)
        self.assertEqual(self.engine.get(run['id'])['current_step'], len(RECIPES['discovery']))

    def test_claim_is_once_with_two_connections(self):
        run = self.engine.create('P-TEST', 'exclusive claim')
        with FactoryStore(self.path) as other_store:
            other = AutomationEngine(other_store)
            self.assertEqual(self.engine.claim('simulation'), run['id'])
            self.assertIsNone(other.claim('simulation'))
        self.assertEqual(self.engine.process(run['id'], SimulationProvider())['state'], 'SIMULATED')

    def test_cross_project_task_not_allowed(self):
        self.store.add_project('P-SECOND', 'second', 'operator')
        self.store.add_task('T-SECOND', 'P-SECOND', 'Task', 'operator')
        with self.assertRaisesRegex(ValueError, 'không thuộc dự án'):
            self.engine.create('P-TEST', 'objective', task_id='T-SECOND')
        with self.assertRaises(ValueError):
            self.engine.create('P-TEST', 'objective', recipe='invalid')
        with self.assertRaises(ValueError):
            self.engine.create('P-TEST', 'objective', provider='shell')
        self.assertEqual(self.engine.list('P-TEST'), [])

    def test_output_tamper_prevents_approval(self):
        run = self.engine.create('P-TEST', 'objective', provider='openai')
        self.engine.run_one('openai', FakeProvider())
        with self.store.db:
            self.store.db.execute('UPDATE automation_outputs SET text=? WHERE run_id=? AND step_no=1', ('tampered', run['id']))
        with self.assertRaisesRegex(ValueError, 'không nguyên vẹn'):
            self.engine.decide(run['id'], 'APPROVED', 'operator')

    def test_durable_across_reopen(self):
        run = self.engine.create('P-TEST', 'durable run', provider='simulation')
        self.engine.run_one('simulation', SimulationProvider())
        with FactoryStore(self.path) as reopened:
            copy = AutomationEngine(reopened).get(run['id'])
            self.assertEqual(copy['state'], 'SIMULATED')
            self.assertEqual(len(copy['outputs']), len(RECIPES['discovery']))

    def test_provider_selection_is_strict(self):
        run = self.engine.create('P-TEST', 'real run', provider='openai')
        self.assertIsNone(self.engine.run_one('simulation', SimulationProvider()))
        self.assertEqual(self.engine.get(run['id'])['state'], 'QUEUED')
        with self.assertRaisesRegex(ValueError, 'Run chưa'):
            self.engine.process(run['id'], FakeProvider())

    def test_no_gate_auto_approve_and_reject(self):
        run = self.engine.create('P-TEST', 'objective', provider='openai')
        self.engine.run_one('openai', FakeProvider())
        self.assertEqual(self.engine.decide(run['id'], 'REJECTED', 'reviewer')['state'], 'REJECTED')
        self.assertTrue(all(g['decision'] == 'PENDING' for g in self.store.gates('P-TEST')))


if __name__ == '__main__':
    unittest.main()
