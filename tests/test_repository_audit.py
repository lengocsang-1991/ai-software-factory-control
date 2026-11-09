"""Tests for the dependency-free static safety preflight."""
import tempfile
import unittest
from pathlib import Path

from scripts.security_audit import ROOT, scan_directory


class RepositorySafetyTests(unittest.TestCase):
    def test_no_local_credentials_in_source_bundle(self):
        self.assertEqual(scan_directory(ROOT), [])

    def test_finds_credentials_and_local_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'export.sqlite').write_text('private')
            (root / 'payload.py').write_text('token = "sk-' + 'A' * 44 + '"')
            findings = scan_directory(root)
            self.assertTrue(any('forbidden-sensitive-file' in f for f in findings))
            self.assertTrue(any('possible-model-api-key' in f for f in findings))


if __name__ == '__main__':
    unittest.main()
