#!/usr/bin/env python3
"""Dependency-free preflight for accidentally published secrets and local data.

This is NOT a substitute for GitHub secret scanning, history review, or pentests.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache'}
FORBIDDEN_SUFFIXES = ('.db', '.sqlite', '.sqlite3', '.db-wal', '.db-shm', '.db-journal', '.pem', '.p12', '.pfx', '.key')
CREDENTIAL_PATTERNS = {
    'private-key': re.compile('-----BEGIN ' + '(?:RSA |EC |OPENSSH )?' + 'PRIVATE KEY-----'),
    'github-token': re.compile(r'\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
    'model-api-key': re.compile(r'\bsk-[A-Za-z0-9_-]{35,}\b'),
    'aws-access-id': re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
}


def scan_directory(root: Path) -> list[str]:
    issues: list[str] = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        if any(part == '.factory-state' for part in path.parts):
            issues.append(f'{rel}: forbidden-local-state')
            continue
        if path.name in ('.env', '.env.local', '.env.production') or (
                path.name.startswith('.env.') and path.name != '.env.example'):
            issues.append(f'{rel}: forbidden-env-file')
            continue
        if path.name.endswith(FORBIDDEN_SUFFIXES):
            issues.append(f'{rel}: forbidden-sensitive-file')
            continue
        if path.stat().st_size > 2_000_000:
            issues.append(f'{rel}: unreviewed-file-over-2MB')
            continue
        try:
            contents = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            issues.append(f'{rel}: unreviewed-binary')
            continue
        for kind, pattern in CREDENTIAL_PATTERNS.items():
            if pattern.search(contents):
                issues.append(f'{rel}: possible-{kind}')
    return issues


def main() -> int:
    problems = scan_directory(ROOT)
    for problem in problems:
        print('FAIL:', problem, file=sys.stderr)
    if problems:
        return 2
    print('PASS: no high-confidence credentials or local state found (working tree only).')
    print('NOTE: verify Git history, GitHub secret scanning and third-party dependencies separately.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
