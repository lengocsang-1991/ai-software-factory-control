#!/usr/bin/env python3
"""Fail-closed GitHub account guard for manual, explicitly authorized publishing.

No network calls, token requests, login or remote mutation are performed.
The caller must obtain --authenticated-login from the actual connected GitHub
account rather than guessing or assuming it from a repository URL.
"""
import argparse
import json
import sys
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / 'INTEGRATIONS' / 'github' / 'target.json'


def check(account, repository=None, config_path=CONFIG):
    config = json.loads(Path(config_path).read_text(encoding='utf-8'))
    target = config['target_owner']
    if not isinstance(account, str) or not account:
        raise ValueError('Chưa xác minh tài khoản GitHub đã đăng nhập.')
    if account != target:
        raise ValueError(f'SAI TÀI KHOẢN: đang kết nối {account!r}, phải là {target!r}. Không thực hiện ghi GitHub.')
    if repository is not None:
        parts = repository.split('/')
        if len(parts) != 2 or parts[0] != target or not parts[1] or not all(c.isalnum() or c in '._-' for c in parts[1]):
            raise ValueError(f'Repository phải thuộc {target} và ở dạng {target}/repo.')
    return {'target_owner': target, 'authenticated_login': account, 'repository': repository, 'account_verified': True,
            'publishing_authorized': False, 'note': 'Chỉ kiểm tra owner/account; KHÔNG cấp quyền push hoặc tạo repository.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Kiểm tra owner GitHub trước khi xin phép phát hành (không gọi API)')
    parser.add_argument('--authenticated-login', required=True, help='Login do GitHub connector cung cấp sau khi xác thực')
    parser.add_argument('--repository', help='owner/repo dự kiến, nếu đã được xác nhận')
    opts = parser.parse_args(argv)
    try:
        print(json.dumps(check(opts.authenticated_login, opts.repository), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f'CHẶN: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
