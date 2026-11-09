"""Durable, opt-in agent analysis workflow engine.

Agents generate review/draft artifacts only. No shell, repo writes, merge, or deployment
capability is available to agent-generated content. Human approval is a hard gate.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .store import FactoryStore, checked_id, required, utc_now

ROLE_PROMPTS = {
    'research': 'Find key questions, hypotheses, constraints, alternatives and explicit unknowns.',
    'business-analysis': 'Write user stories, functional requirements and measurable acceptance criteria.',
    'product-management': 'Prioritize scope, milestones and business value; identify trade-offs.',
    'architecture': 'Propose components, data flows, interfaces, reliability and architecture decisions.',
    'ui-ux': 'Review interaction flows, responsive layouts, accessibility and failure states.',
    'frontend': 'Plan frontend implementation and tests; do not claim code has been written.',
    'backend': 'Plan backend interfaces, authorization, error handling and tests.',
    'database': 'Specify schema, transactions, backup and migration risks.',
    'testing': 'Design test cases, coverage gaps and evidence needed; do not invent results.',
    'security': 'Review threats, privacy, secrets, permissions and mitigations.',
    'code-review': 'List maintainability checks and code review risks, without claiming to have audited unseen source.',
    'devops': 'Specify safe CI/CD gates, rollback, observability and release requirements.',
    'audit': 'Independently flag unsupported claims, missing proof and unresolved risk.',
    'documentation': 'Draft documentation and record verified versus proposed functionality.',
    'operations': 'Recommend monitoring, incident response and runbook requirements.',
    'optimization': 'Identify bottlenecks and safe incremental optimization experiments.',
}

# Each recipe is explicit and deterministic. A role generates only text artifacts.
RECIPES = {
    'discovery': ('research', 'business-analysis', 'product-management', 'architecture', 'testing', 'security', 'audit'),
    'design-review': ('architecture', 'ui-ux', 'frontend', 'backend', 'database', 'security', 'testing', 'audit'),
    'full-review': tuple(ROLE_PROMPTS),
}
RUN_STATES = ('QUEUED', 'RUNNING', 'WAITING_APPROVAL', 'APPROVED', 'REJECTED', 'FAILED', 'SIMULATED')


@dataclass(frozen=True)
class Generation:
    text: str
    model: str
    simulated: bool = False


class AgentProvider(Protocol):
    def generate(self, role: str, instruction: str, objective: str, context: str) -> Generation: ...


class SimulationProvider:
    """Explicitly labeled fake provider; cannot receive human approval as real output."""
    def generate(self, role: str, instruction: str, objective: str, context: str) -> Generation:
        return Generation(
            text=f'[SIMULATED — NOT VERIFIED]\nRole: {role}\nObjective: {objective[:240]}\nChecklist: {instruction}',
            model='simulation', simulated=True,
        )


class AutomationEngine:
    def __init__(self, store: FactoryStore):
        self.store = store
        self.db = store.db
        with self.db:
            self.db.executescript('''
              CREATE TABLE IF NOT EXISTS automation_runs (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL REFERENCES projects(id),
                task_id TEXT REFERENCES tasks(id),
                objective TEXT NOT NULL,
                recipe TEXT NOT NULL,
                provider TEXT NOT NULL CHECK(provider IN ('simulation','openai','gemini')),
                state TEXT NOT NULL,
                current_step INTEGER NOT NULL DEFAULT 0,
                error_code TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                approved_by TEXT NOT NULL DEFAULT '',
                approval_note TEXT NOT NULL DEFAULT ''
              );
              CREATE TABLE IF NOT EXISTS automation_outputs (
                run_id TEXT NOT NULL REFERENCES automation_runs(id),
                step_no INTEGER NOT NULL,
                role TEXT NOT NULL,
                model TEXT NOT NULL,
                text TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                simulated INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY(run_id, step_no)
              );
              CREATE INDEX IF NOT EXISTS idx_automation_pending ON automation_runs(provider,state,created_at);
            ''')

    def create(self, project_id: str, objective: str, recipe: str = 'discovery',
               provider: str = 'simulation', task_id: str | None = None) -> dict:
        self.store._project_required(project_id)
        if recipe not in RECIPES:
            raise ValueError('Recipe không hợp lệ')
        if provider not in ('simulation', 'openai', 'gemini'):
            raise ValueError('Provider không được phép')
        objective = required(objective, 'mục tiêu')
        if len(objective) > 4000:
            raise ValueError('Mục tiêu vượt giới hạn 4000 ký tự')
        if task_id:
            task = self.store.task(task_id)
            if not task or task['project_id'] != project_id:
                raise ValueError('Nhiệm vụ không thuộc dự án')
        run_id = 'RUN-' + uuid.uuid4().hex[:20]
        checked_id(run_id)
        now = utc_now()
        with self.db:
            self.db.execute('''INSERT INTO automation_runs
                (id,project_id,task_id,objective,recipe,provider,state,created_at,updated_at)
                VALUES(?,?,?,?,?,?,'QUEUED',?,?)''',
                (run_id, project_id, task_id, objective, recipe, provider, now, now))
            self.store._event(project_id, 'AUTOMATION_ENQUEUED', {'run_id': run_id, 'recipe': recipe, 'provider': provider})
        return self.get(run_id, with_outputs=False)

    def get(self, run_id: str, with_outputs: bool = True) -> dict:
        checked_id(run_id)
        row = self.db.execute('SELECT * FROM automation_runs WHERE id=?', (run_id,)).fetchone()
        if row is None:
            raise ValueError('Không tìm thấy run')
        result = dict(row)
        result['steps_total'] = len(RECIPES[result['recipe']])
        if with_outputs:
            result['outputs'] = [dict(x) for x in self.db.execute(
                'SELECT * FROM automation_outputs WHERE run_id=? ORDER BY step_no', (run_id,)
            )]
        return result

    def list(self, project_id: str) -> list[dict]:
        self.store._project_required(project_id)
        ids = [r['id'] for r in self.db.execute('SELECT id FROM automation_runs WHERE project_id=? ORDER BY created_at,id', (project_id,))]
        return [self.get(x, with_outputs=False) for x in ids]

    def claim(self, provider: str) -> str | None:
        if provider not in ('simulation','openai','gemini'):
            raise ValueError('Provider không hợp lệ')
        # Acquire SQLite write lock before selecting to prevent duplicate claims.
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.db.execute('''SELECT id, project_id FROM automation_runs
                WHERE state='QUEUED' AND provider=? ORDER BY created_at,id LIMIT 1''', (provider,)).fetchone()
            if not row:
                self.db.commit()
                return None
            self.db.execute("UPDATE automation_runs SET state='RUNNING',updated_at=? WHERE id=? AND state='QUEUED'", (utc_now(), row['id']))
            self.store._event(row['project_id'], 'AUTOMATION_CLAIMED', {'run_id': row['id']})
            self.db.commit()
            return str(row['id'])
        except Exception:
            self.db.rollback()
            raise

    def process(self, run_id: str, provider: AgentProvider) -> dict:
        run = self.get(run_id, with_outputs=False)
        if run['state'] != 'RUNNING':
            raise ValueError('Run chưa được claim hoặc không trong trạng thái RUNNING')
        roles = RECIPES[run['recipe']]
        for idx in range(run['current_step'], len(roles)):
            role = roles[idx]
            history = self.db.execute('''SELECT role,text FROM automation_outputs
                WHERE run_id=? ORDER BY step_no DESC LIMIT 2''', (run_id,)).fetchall()
            context = '\n'.join(f'{r["role"]}: {r["text"][:1200]}' for r in reversed(history))
            try:
                result = provider.generate(role, ROLE_PROMPTS[role], run['objective'], context)
                if not isinstance(result, Generation) or not result.text.strip():
                    raise ValueError('EMPTY_GENERATION')
                if len(result.text) > 12000:
                    raise ValueError('OUTPUT_LIMIT_EXCEEDED')
                content_hash = hashlib.sha256(result.text.encode('utf-8')).hexdigest()
                with self.db:
                    self.db.execute('''INSERT INTO automation_outputs
                        (run_id,step_no,role,model,text,sha256,simulated,created_at)
                        VALUES(?,?,?,?,?,?,?,?)''',
                        (run_id, idx + 1, role, result.model[:100], result.text, content_hash,
                         1 if result.simulated else 0, utc_now()))
                    self.db.execute('''UPDATE automation_runs SET current_step=?,updated_at=? WHERE id=?''',
                                    (idx + 1, utc_now(), run_id))
                    self.store._event(run['project_id'], 'AUTOMATION_STEP', {'run_id': run_id, 'role': role, 'step': idx + 1,
                                                                            'sha256': content_hash, 'simulated': result.simulated})
            except Exception as exc:
                # Avoid storing exception strings containing potentially sensitive provider credentials.
                with self.db:
                    self.db.execute("UPDATE automation_runs SET state='FAILED',error_code=?,updated_at=? WHERE id=?",
                                    (type(exc).__name__[:80], utc_now(), run_id))
                    self.store._event(run['project_id'], 'AUTOMATION_FAILED', {'run_id': run_id, 'step': idx + 1,
                                                                            'error_code': type(exc).__name__})
                return self.get(run_id, with_outputs=False)
        has_simulated = bool(self.db.execute(
            'SELECT 1 FROM automation_outputs WHERE run_id=? AND simulated=1 LIMIT 1', (run_id,)
        ).fetchone())
        final = 'SIMULATED' if has_simulated else 'WAITING_APPROVAL'
        with self.db:
            self.db.execute('UPDATE automation_runs SET state=?,updated_at=? WHERE id=?', (final, utc_now(), run_id))
            self.store._event(run['project_id'], 'AUTOMATION_REVIEW_READY', {'run_id': run_id, 'state': final})
        return self.get(run_id, with_outputs=False)

    def run_one(self, provider_name: str, provider: AgentProvider) -> dict | None:
        run_id = self.claim(provider_name)
        if run_id is None:
            return None
        return self.process(run_id, provider)

    def retry(self, run_id: str) -> dict:
        run = self.get(run_id, with_outputs=False)
        if run['state'] != 'FAILED':
            raise ValueError('Chỉ retry run FAILED; không tự phục hồi RUNNING khi chưa kiểm tra')
        with self.db:
            self.db.execute("UPDATE automation_runs SET state='QUEUED',error_code='',updated_at=? WHERE id=?", (utc_now(), run_id))
            self.store._event(run['project_id'], 'AUTOMATION_REQUEUED', {'run_id': run_id})
        return self.get(run_id, with_outputs=False)

    def decide(self, run_id: str, decision: str, actor: str, note: str = '') -> dict:
        run = self.get(run_id)
        if run['state'] != 'WAITING_APPROVAL':
            raise ValueError('Chỉ phê duyệt run đã sinh đủ báo cáo thực và chờ duyệt')
        if decision not in ('APPROVED', 'REJECTED'):
            raise ValueError('Quyết định không hợp lệ')
        actor = required(actor, 'người phê duyệt')
        if len(note) > 2000:
            raise ValueError('Ghi chú quá dài')
        if len(run['outputs']) != run['steps_total']:
            raise ValueError('Thiếu đầu ra Agent')
        for output in run['outputs']:
            if hashlib.sha256(output['text'].encode('utf-8')).hexdigest() != output['sha256'] or output['simulated']:
                raise ValueError('Đầu ra Agent không nguyên vẹn hoặc mô phỏng')
        with self.db:
            self.db.execute('''UPDATE automation_runs SET state=?,approved_by=?,approval_note=?,updated_at=? WHERE id=?''',
                            (decision, actor, note, utc_now(), run_id))
            self.store._event(run['project_id'], 'AUTOMATION_DECIDED', {'run_id': run_id, 'decision': decision, 'actor': actor})
        return self.get(run_id, with_outputs=False)

    def output_manifest(self, run_id: str) -> dict:
        run = self.get(run_id)
        return {'run_id': run_id, 'state': run['state'], 'recipe': run['recipe'],
                'steps': [{'role': r['role'], 'sha256': r['sha256'], 'model': r['model'],
                           'simulated': bool(r['simulated'])} for r in run['outputs']],
                'notice': 'SHA-256 xác nhận nội dung trong SQLite, không xác minh tính đúng đắn hoặc danh tính người duyệt.'}
