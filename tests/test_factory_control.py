"""Functional/negative tests using disposable local data only."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from factory_control.store import FactoryStore, GATE_KINDS

ROOT = Path(__file__).resolve().parents[1]


class FactoryControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.store = FactoryStore(self.home / "state.sqlite")
        self.addCleanup(self.store.close)
        self.store.add_project("P-100", "Dự án thử nghiệm", "operator")

    def file(self, filename="proof.txt", content="synthetic proof"):
        p = self.home / filename
        p.write_text(content, encoding="utf-8")
        return p

    def test_project_is_local_and_persistent(self):
        p = self.store.project("P-100")
        self.assertEqual(p["stage"], 1)
        self.assertEqual(p["status"], "ACTIVE")
        self.assertEqual(len(self.store.projects()), 1)
        with FactoryStore(self.home / "state.sqlite") as another:
            self.assertEqual(another.project("P-100")["name"], "Dự án thử nghiệm")

    def test_duplicate_project_fails_without_overwrite(self):
        with self.assertRaises(Exception):
            self.store.add_project("P-100", "Trùng", "operator")
        self.assertEqual(self.store.project("P-100")["name"], "Dự án thử nghiệm")

    def test_task_done_requires_matching_evidence(self):
        self.store.add_task("T-101", "P-100", "Xây dựng", "agent")
        for s in ["READY", "IN_PROGRESS", "TESTING", "WAITING_APPROVAL"]:
            self.store.change_task_status("T-101", s)
        with self.assertRaisesRegex(ValueError, "bằng chứng"):
            self.store.change_task_status("T-101", "DONE")
        e = self.store.add_evidence("P-100", "OTHER", self.file(), task_id="T-101")
        self.assertEqual(self.store.change_task_status("T-101", "DONE", e["id"])["status"], "DONE")
        with self.assertRaisesRegex(ValueError, "Không thể chuyển"):
            self.store.change_task_status("T-101", "READY")

    def test_task_evidence_cannot_cross_project(self):
        self.store.add_project("P-200", "Khác", "operator")
        self.store.add_task("T-101", "P-100", "Xây dựng", "agent")
        self.store.add_task("T-202", "P-200", "Thử", "other")
        with self.assertRaisesRegex(ValueError, "đúng nhiệm vụ"):
            self.store.add_evidence("P-100", "OTHER", self.file(), task_id="T-202")

    def test_gate_cannot_skip_or_use_wrong_evidence(self):
        e = self.store.add_evidence("P-100", "PRODUCT_BRIEF", self.file())
        with self.assertRaisesRegex(ValueError, "giai đoạn hiện tại"):
            self.store.decide_gate("P-100", 2, "APPROVED", "operator", e["id"])
        with self.assertRaisesRegex(ValueError, "GATE 1 chưa"):
            self.store.advance("P-100")
        with self.assertRaisesRegex(ValueError, "yêu cầu bằng chứng loại"):
            other = self.store.add_evidence("P-100", "OTHER", self.file("other.txt"))
            self.store.decide_gate("P-100", 1, "APPROVED", "operator", other["id"])
        self.store.decide_gate("P-100", 1, "REJECTED", "operator", e["id"])
        with self.assertRaisesRegex(ValueError, "chưa được phê duyệt"):
            self.store.advance("P-100")
        self.store.decide_gate("P-100", 1, "APPROVED", "operator", e["id"])
        self.assertEqual(self.store.advance("P-100")["stage"], 2)

    def test_evidence_tamper_blocks_gate_and_done(self):
        src = self.file()
        e = self.store.add_evidence("P-100", "PRODUCT_BRIEF", src)
        self.assertEqual(e["sha256"], hashlib.sha256(src.read_bytes()).hexdigest())
        src.write_text("changed", encoding="utf-8")
        self.assertFalse(self.store.verify_evidence(e["id"])["valid"])
        with self.assertRaisesRegex(ValueError, "không còn nguyên vẹn"):
            self.store.decide_gate("P-100", 1, "APPROVED", "operator", e["id"])

    def test_all_gates_in_order_complete_in_sandbox(self):
        for num, kind in enumerate(GATE_KINDS, 1):
            ev = self.store.add_evidence("P-100", kind, self.file(f"gate-{num}.txt", f"synthetic {num}"))
            self.store.decide_gate("P-100", num, "APPROVED", "test-fixture", ev["id"])
            self.store.advance("P-100")
        self.assertEqual(self.store.project("P-100")["status"], "COMPLETE")
        self.assertEqual(self.store.project("P-100")["stage"], 8)
        self.assertEqual(len(self.store.events("P-100")), 1 + 8 * 3)
        self.assertEqual(len(self.store.report("P-100")["gates"]), 8)
        with self.assertRaisesRegex(ValueError, "đã hoàn tất"):
            self.store.advance("P-100")

    def test_foreign_evidence_cannot_approve(self):
        self.store.add_project("P-200", "Khác", "operator")
        e = self.store.add_evidence("P-200", "PRODUCT_BRIEF", self.file())
        with self.assertRaisesRegex(ValueError, "không thuộc dự án"):
            self.store.decide_gate("P-100", 1, "APPROVED", "operator", e["id"])

    def test_invalid_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "ID cần"):
            self.store.add_task("x/../../oops", "P-100", "Nhiệm vụ", "operator")
        with self.assertRaisesRegex(ValueError, "Repository"):
            self.store.add_project("P-200", "Khác", "operator", repository="https://example.com/repo")
        with self.assertRaisesRegex(ValueError, "Không thể chuyển"):
            self.store.add_task("T-101", "P-100", "Nhiệm vụ", "operator")
            self.store.change_task_status("T-101", "DONE")

    def test_cli_smoke(self):
        db = self.home / "cli.sqlite"
        cmd = [sys.executable, "-m", "factory_control", "--db", str(db)]
        for args in [["init"], ["project", "add", "--id", "CL-1", "--name", "Ứng dụng", "--owner", "operator"], ["project", "list"]]:
            result = subprocess.run(cmd + args, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIsNotNone(json.loads(result.stdout))
        result = subprocess.run(cmd + ["project", "advance", "--id", "CL-1"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("chưa được phê duyệt", result.stderr)

    def test_no_default_projects_or_fake_approvals(self):
        with FactoryStore(self.home / "empty.sqlite") as empty:
            self.assertEqual(empty.projects(), [])
        self.assertTrue(all(g["decision"] == "PENDING" for g in self.store.gates("P-100")))


if __name__ == "__main__":
    unittest.main()
