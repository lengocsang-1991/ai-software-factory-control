"""No network or secrets involved: prevent publishing under the wrong account."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_github_target import check


class GitHubTargetTests(unittest.TestCase):
    def test_only_designated_owner_is_accepted(self):
        with self.assertRaisesRegex(ValueError, 'SAI TÀI KHOẢN'):
            check('traingheoxaqueht123')
        data = check('lengocsang-1991', 'lengocsang-1991/ai-software-factory-control')
        self.assertTrue(data['account_verified'])
        self.assertFalse(data['publishing_authorized'])

    def test_reject_repository_of_other_owner(self):
        with self.assertRaisesRegex(ValueError, 'Repository phải thuộc'):
            check('lengocsang-1991', 'traingheoxaqueht123/any-repo')

    def test_missing_login_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'Chưa xác minh'):
            check('')


if __name__ == '__main__':
    unittest.main()
