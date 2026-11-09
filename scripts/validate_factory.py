#!/usr/bin/env python3
"""Static validation; no network calls, credentials, or external dependencies."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
def readjson(rel):
    p=ROOT/rel
    assert p.exists(), f'Missing: {rel}'
    with p.open(encoding='utf-8') as f: return json.load(f)

workflow=readjson('CONTROL/workflow-engine/workflow.json')
agents=readjson('AGENTS/registry.json')
gates=readjson('CONTROL/approval-gates/quality-gates.json')
projects=readjson('CONTROL/project-registry/projects.json')
tasks=readjson('CONTROL/task-manager/tasks.json')
assert len(workflow['stages']) == 8
assert [x['order'] for x in workflow['stages']] == list(range(1,9))
assert len(agents['agents']) == 16
assert len({x['id'] for x in agents['agents']}) == 16
from factory_control.automation import ROLE_PROMPTS, RECIPES
assert {x['slug'] for x in agents['agents']} == set(ROLE_PROMPTS)
assert len(RECIPES['full-review']) == 16
assert all(x['status'] == 'TEXT_ANALYSIS_RUNTIME_AVAILABLE_PROVIDER_REQUIRED' for x in agents['agents'])
assert len(gates['gates']) == 8
assert [x['gate'] for x in workflow['stages']] == [x['id'] for x in gates['gates']]
assert isinstance(projects['projects'],list) and isinstance(tasks['tasks'],list)
assert 'DONE' in tasks['valid_statuses'] and 'NOT_VERIFIED' in tasks['valid_statuses']
for x in workflow['stages']: assert (ROOT/'WORKFLOWS'/x['id']/'stage.md').exists()
for x in agents['agents']: assert (ROOT/'AGENTS'/x['slug']/'AGENT.md').exists()
for rel in ('README.md','INTEGRATIONS/github/SETUP.md','SECURITY/policies/SECURITY.md','DOCUMENTATION/operating-guides/level-roadmap.md', 'factory_control/cli.py', 'factory_control/store.py', 'factory_control/web.py', 'factory_control/automation.py', 'factory_control/providers.py', 'factory_control/github_intake.py', 'factory_control/static/index.html', 'tests/test_factory_control.py', '.github/workflows/ci.yml'):
    assert (ROOT/rel).exists(), rel
print('PASS: 16 agent definitions, 8 stages, 8 gates, JSON registries, templates and policy files present.')
print('NOTE: This command validates structure only. Run python -m unittest discover -s tests -v separately.')
