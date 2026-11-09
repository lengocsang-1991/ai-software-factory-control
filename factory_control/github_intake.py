"""GitHub issue intake: READ-ONLY remote access, idempotent local task creation.

Only explicitly labeled issues authored by the designated repository owner are eligible.
Does not execute issue content, post comments, commit code, or change remote issues.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request

from .automation import AutomationEngine
from .store import FactoryStore

OWNER = 'lengocsang-1991'
ISSUE_LABEL = 'factory:ready'
REPO_RE = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
MAX_ISSUE_PAGES = 3


def get_approved_issues(repository: str, token: str | None = None) -> list[dict]:
    if not REPO_RE.fullmatch(repository or '') or repository.split('/')[0].lower() != OWNER:
        raise ValueError('GitHub intake bị giới hạn trong repository của lengocsang-1991')
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'ai-software-factory/1.3'}
    token = token or os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    accepted = []
    for page in range(1, MAX_ISSUE_PAGES + 1):
        # Construct each page locally. Never follow an untrusted Link-header URL.
        url = (f'https://api.github.com/repos/{repository}/issues'
               f'?state=open&labels=factory%3Aready&per_page=100&page={page}')
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status != 200:
                    raise RuntimeError('GITHUB_HTTP_ERROR')
                payload = response.read(2_000_001)
                response_headers = getattr(response, 'headers', None)
                link = (response_headers.get('Link', '') if response_headers else '') or ''
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError('GITHUB_UNAVAILABLE') from None
        if len(payload) > 2_000_000:
            raise RuntimeError('GITHUB_RESPONSE_TOO_LARGE')
        try:
            data = json.loads(payload)
        except (ValueError, UnicodeError):
            raise RuntimeError('GITHUB_INVALID_RESPONSE') from None
        if not isinstance(data, list):
            raise RuntimeError('GITHUB_UNEXPECTED_RESPONSE')
        for issue in data:
            if not isinstance(issue, dict) or 'pull_request' in issue:
                continue
            if type(issue.get('number')) is not int or issue['number'] < 1:
                continue
            author = issue.get('user')
            if not isinstance(author, dict) or str(author.get('login', '')).lower() != OWNER:
                continue
            raw_labels = issue.get('labels')
            labels = [x.get('name') for x in raw_labels if isinstance(x, dict)] if isinstance(raw_labels, list) else []
            if ISSUE_LABEL not in labels:
                continue
            title = str(issue.get('title') or '').strip()
            if not title:
                continue
            accepted.append({'number': issue['number'], 'title': title[:220],
                             'body': str(issue.get('body') or '')[:1600],
                             'html_url': f'https://github.com/{repository}/issues/{issue["number"]}'})
        has_more = bool(re.search(r'rel=["\']next["\']', link))
        if not has_more:
            break
        if page == MAX_ISSUE_PAGES:
            # Never silently ignore the rest of the issues.
            raise RuntimeError('GITHUB_TOO_MANY_ISSUES')
    return accepted


def ingest(store: FactoryStore, project_id: str, *, enqueue: bool = False,
           provider: str = 'simulation', token: str | None = None) -> list[dict]:
    project = store._project_required(project_id)
    repo = project.get('repository')
    if not repo:
        raise ValueError('Dự án chưa khai báo repository')
    if provider not in ('simulation', 'openai', 'gemini'):
        raise ValueError('Provider không được hỗ trợ')
    accepted = get_approved_issues(repo, token=token)
    automation = AutomationEngine(store)
    results = []
    prefix = hashlib.sha256(project_id.encode()).hexdigest()[:8]
    for issue in accepted:
        task_id = f'GH-{prefix}-{issue["number"]}'
        existing = store.task(task_id)
        if not existing:
            store.add_task(task_id, project_id, issue['title'], OWNER,
                           description=f'{issue["html_url"]}\n{issue["body"]}')
        elif existing['project_id'] != project_id:
            raise ValueError('Xung đột mã nhiệm vụ GitHub')
        new_run = None
        if enqueue:
            found = store.db.execute('SELECT id FROM automation_runs WHERE task_id=? LIMIT 1', (task_id,)).fetchone()
            if not found:
                obj = f'GitHub issue (untrusted input): {issue["title"]}\n{issue["body"]}'
                new_run = automation.create(project_id, obj[:3500], provider=provider, task_id=task_id)['id']
        results.append({'issue': issue['number'], 'task_id': task_id,
                        'created': existing is None, 'run_enqueued': new_run})
    return results
