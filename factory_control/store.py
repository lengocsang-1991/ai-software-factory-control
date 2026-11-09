"""Transactional local project/task/gate registry with audit events (stdlib SQLite)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

STATUSES = (
    "BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "TESTING", "AUDITING",
    "WAITING_APPROVAL", "DONE", "FAILED", "NOT_VERIFIED",
)
PRIORITIES = ("LOW", "NORMAL", "HIGH", "CRITICAL")
GATE_KINDS = (
    "PRODUCT_BRIEF", "SPEC", "DESIGN", "BUILD", "TEST_REPORT",
    "AUDIT_REPORT", "RELEASE_APPROVAL", "DEPLOYMENT_REPORT",
)
TRANSITIONS = {
    "BACKLOG": {"READY", "BLOCKED", "NOT_VERIFIED"},
    "READY": {"IN_PROGRESS", "BLOCKED", "NOT_VERIFIED"},
    "IN_PROGRESS": {"TESTING", "AUDITING", "WAITING_APPROVAL", "BLOCKED", "FAILED", "NOT_VERIFIED"},
    "TESTING": {"IN_PROGRESS", "AUDITING", "WAITING_APPROVAL", "BLOCKED", "FAILED", "NOT_VERIFIED"},
    "AUDITING": {"IN_PROGRESS", "WAITING_APPROVAL", "BLOCKED", "FAILED", "NOT_VERIFIED"},
    "WAITING_APPROVAL": {"DONE", "IN_PROGRESS", "BLOCKED", "FAILED", "NOT_VERIFIED"},
    "BLOCKED": {"READY", "IN_PROGRESS", "FAILED", "NOT_VERIFIED"},
    "FAILED": {"READY", "IN_PROGRESS", "NOT_VERIFIED"},
    "NOT_VERIFIED": {"BACKLOG", "READY", "IN_PROGRESS", "BLOCKED"},
    "DONE": set(),
}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,63}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def checked_id(value: str) -> str:
    if not ID_RE.fullmatch(value or ""):
        raise ValueError("ID cần 2–64 ký tự: chữ, số, dấu chấm, gạch nối hoặc gạch dưới")
    return value


def required(value: str, name: str) -> str:
    clean = (value or "").strip()
    if not clean:
        raise ValueError(f"Thiếu {name}")
    if len(clean) > 5000:
        raise ValueError(f"{name} quá dài")
    return clean


def row_dict(row):
    return dict(row) if row is not None else None


class FactoryStore:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path).expanduser().resolve()
        new_directory = not self.path.parent.exists()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if new_directory and os.name != "nt":
            os.chmod(self.path.parent, 0o700)
        self.db = sqlite3.connect(self.path, timeout=15)
        if os.name != "nt":
            os.chmod(self.path, 0o600)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=15000")
        self._create_schema()

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @contextmanager
    def _write_locked(self):
        """Acquire the write lock before checking a state transition.

        `with self.db` alone only begins the transaction at the first write,
        which previously allowed two processes to validate stale state.
        """
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _create_schema(self):
        with self.db:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
                    owner TEXT NOT NULL, repository TEXT, stage INTEGER NOT NULL DEFAULT 1 CHECK(stage BETWEEN 1 AND 8),
                    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE','COMPLETE')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
                    title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', owner TEXT NOT NULL,
                    priority TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'BACKLOG',
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL REFERENCES projects(id),
                    task_id TEXT REFERENCES tasks(id), kind TEXT NOT NULL,
                    source_path TEXT NOT NULL, file_name TEXT NOT NULL,
                    sha256 TEXT NOT NULL, byte_count INTEGER NOT NULL,
                    note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS gates (
                    project_id TEXT NOT NULL REFERENCES projects(id),
                    gate_number INTEGER NOT NULL CHECK(gate_number BETWEEN 1 AND 8),
                    decision TEXT NOT NULL CHECK(decision IN ('APPROVED','REJECTED')),
                    approver TEXT NOT NULL, evidence_id INTEGER NOT NULL REFERENCES evidence(id),
                    note TEXT NOT NULL DEFAULT '', decided_at TEXT NOT NULL,
                    PRIMARY KEY(project_id, gate_number)
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL REFERENCES projects(id),
                    action TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
                CREATE INDEX IF NOT EXISTS idx_evidence_project ON evidence(project_id);
                CREATE INDEX IF NOT EXISTS idx_events_project ON events(project_id);
            """)

    def _event(self, project: str, action: str, detail: dict):
        self.db.execute(
            "INSERT INTO events (project_id, action, detail, created_at) VALUES (?,?,?,?)",
            (project, action, json.dumps(detail, ensure_ascii=False, sort_keys=True), utc_now()),
        )

    def project(self, project_id):
        return row_dict(self.db.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone())

    def _project_required(self, project_id):
        result = self.project(project_id)
        if not result:
            raise ValueError(f"Không tìm thấy dự án {project_id}")
        return result

    def add_project(self, project_id, name, owner, description="", repository=None):
        checked_id(project_id)
        name, owner = required(name, "tên dự án"), required(owner, "người phụ trách")
        repository = repository.strip() if repository else None
        if repository and not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("Repository phải ở dạng owner/repo")
        now = utc_now()
        with self.db:
            self.db.execute(
                "INSERT INTO projects(id,name,description,owner,repository,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (project_id, name, description, owner, repository, now, now),
            )
            self._event(project_id, "PROJECT_CREATED", {"name": name, "owner": owner})
        return self.project(project_id)

    def projects(self):
        return [dict(r) for r in self.db.execute("SELECT * FROM projects ORDER BY created_at,id")]

    def add_task(self, task_id, project_id, title, owner, priority="NORMAL", description=""):
        checked_id(task_id)
        self._project_required(project_id)
        if priority not in PRIORITIES:
            raise ValueError("Mức ưu tiên không hợp lệ")
        now = utc_now()
        with self.db:
            self.db.execute(
                "INSERT INTO tasks(id,project_id,title,description,owner,priority,status,created_at,updated_at) "
                "VALUES(?,?,?,?,? ,?,'BACKLOG',?,?)",
                (task_id, project_id, required(title, "tên nhiệm vụ"), description, required(owner, "người phụ trách"), priority, now, now),
            )
            self._event(project_id, "TASK_CREATED", {"task_id": task_id})
        return self.task(task_id)

    def task(self, task_id):
        return row_dict(self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())

    def tasks(self, project_id):
        self._project_required(project_id)
        return [dict(r) for r in self.db.execute("SELECT * FROM tasks WHERE project_id=? ORDER BY created_at,id", (project_id,))]

    def evidence(self, evidence_id):
        return row_dict(self.db.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone())

    def add_evidence(self, project_id, kind, file_path, note="", task_id=None):
        self._project_required(project_id)
        if kind not in set(GATE_KINDS) | {"OTHER"}:
            raise ValueError(f"Loại bằng chứng cần thuộc: {', '.join(GATE_KINDS)} hoặc OTHER")
        if task_id:
            task = self.task(task_id)
            if not task or task["project_id"] != project_id:
                raise ValueError("Bằng chứng phải thuộc đúng nhiệm vụ và dự án")
        src = Path(file_path).expanduser().resolve(strict=True)
        if not src.is_file():
            raise ValueError("Bằng chứng phải là tệp hiện hữu")
        if src.stat().st_size > 200 * 1024 * 1024:
            raise ValueError("Tệp vượt 200 MB; cần cơ chế lưu trữ bằng chứng riêng")
        digest = hashlib.sha256()
        size = 0
        with src.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        with self.db:
            cur = self.db.execute(
                "INSERT INTO evidence(project_id,task_id,kind,source_path,file_name,sha256,byte_count,note,created_at) "
                "VALUES(?,?,?,?,?,?,?,?,?)",
                (project_id, task_id, kind, str(src), src.name, digest.hexdigest(), size, note, utc_now()),
            )
            self._event(project_id, "EVIDENCE_RECORDED", {"evidence_id": cur.lastrowid, "kind": kind, "task_id": task_id})
            evidence_id = cur.lastrowid
        return self.evidence(evidence_id)

    def evidence_list(self, project_id):
        self._project_required(project_id)
        return [dict(r) for r in self.db.execute(
            "SELECT * FROM evidence WHERE project_id=? ORDER BY id", (project_id,)
        )]

    def verify_evidence(self, evidence_id):
        evidence = self.evidence(evidence_id)
        if not evidence:
            raise ValueError("Không tồn tại bằng chứng")
        src = Path(evidence["source_path"])
        if not src.is_file():
            return {"id": evidence_id, "valid": False, "reason": "FILE_MISSING"}
        digest = hashlib.sha256()
        size = 0
        with src.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        valid = digest.hexdigest() == evidence['sha256'] and size == evidence['byte_count']
        return {"id": evidence_id, "valid": valid,
                "reason": "HASH_MATCH" if valid else "HASH_OR_SIZE_MISMATCH"}

    def change_task_status(self, task_id, new_status, evidence_id=None):
        with self._write_locked():
            task = self.task(task_id)
            if not task:
                raise ValueError(f"Không tìm thấy nhiệm vụ {task_id}")
            if new_status not in STATUSES:
                raise ValueError("Trạng thái nhiệm vụ không hợp lệ")
            if new_status not in TRANSITIONS[task["status"]]:
                raise ValueError(f"Không thể chuyển {task['status']} → {new_status}")
            if new_status == "DONE":
                if evidence_id is None:
                    raise ValueError("DONE bắt buộc có bằng chứng (--evidence-id)")
                evidence = self.evidence(evidence_id)
                if not evidence or evidence["project_id"] != task["project_id"] or evidence["task_id"] != task_id:
                    raise ValueError("Bằng chứng DONE phải gắn đúng nhiệm vụ")
                if not self.verify_evidence(evidence_id)["valid"]:
                    raise ValueError("Bằng chứng DONE không tồn tại hoặc đã bị thay đổi")
            self.db.execute("UPDATE tasks SET status=?,updated_at=? WHERE id=?", (new_status, utc_now(), task_id))
            self._event(task["project_id"], "TASK_STATUS_CHANGED", {"task_id": task_id, "from": task["status"], "to": new_status, "evidence_id": evidence_id})
        return self.task(task_id)

    def gates(self, project_id):
        self._project_required(project_id)
        decisions = {r["gate_number"]: dict(r) for r in self.db.execute(
            "SELECT * FROM gates WHERE project_id=?", (project_id,)
        )}
        return [decisions.get(i, {"project_id": project_id, "gate_number": i, "decision": "PENDING"}) for i in range(1, 9)]

    def decide_gate(self, project_id, gate_number, decision, approver, evidence_id, note=""):
        with self._write_locked():
            project = self._project_required(project_id)
            if project["status"] == "COMPLETE":
                raise ValueError("Dự án đã hoàn tất, không thể thay đổi cổng")
            if gate_number != project["stage"]:
                raise ValueError("Chỉ được quyết định cổng của giai đoạn hiện tại")
            if decision not in ("APPROVED", "REJECTED"):
                raise ValueError("Chỉ chấp nhận APPROVED hoặc REJECTED")
            ev = self.evidence(evidence_id)
            if not ev or ev["project_id"] != project_id:
                raise ValueError("Bằng chứng không thuộc dự án")
            if ev["kind"] != GATE_KINDS[gate_number - 1]:
                raise ValueError(f"GATE {gate_number} yêu cầu bằng chứng loại {GATE_KINDS[gate_number - 1]}")
            if not self.verify_evidence(evidence_id)["valid"]:
                raise ValueError("Bằng chứng không còn nguyên vẹn")
            approver = required(approver, "người phê duyệt")
            self.db.execute(
                "INSERT INTO gates(project_id,gate_number,decision,approver,evidence_id,note,decided_at) "
                "VALUES(?,?,?,?,?,?,?) ON CONFLICT(project_id,gate_number) DO UPDATE SET "
                "decision=excluded.decision,approver=excluded.approver,evidence_id=excluded.evidence_id, "
                "note=excluded.note,decided_at=excluded.decided_at",
                (project_id, gate_number, decision, approver, evidence_id, note, utc_now()),
            )
            self._event(project_id, "GATE_DECIDED", {"gate": gate_number, "decision": decision, "approver": approver, "evidence_id": evidence_id})
        return self.gates(project_id)[gate_number - 1]

    def advance(self, project_id):
        with self._write_locked():
            project = self._project_required(project_id)
            if project["status"] == "COMPLETE":
                raise ValueError("Dự án đã hoàn tất")
            stage = project["stage"]
            gate = self.gates(project_id)[stage - 1]
            if gate["decision"] != "APPROVED":
                raise ValueError(f"GATE {stage} chưa được phê duyệt")
            if not self.verify_evidence(gate["evidence_id"])["valid"]:
                raise ValueError("Bằng chứng phê duyệt không còn nguyên vẹn")
            if stage == 8:
                self.db.execute("UPDATE projects SET status='COMPLETE',updated_at=? WHERE id=?", (utc_now(), project_id))
                self._event(project_id, "PROJECT_COMPLETED", {"gate": stage})
            else:
                self.db.execute("UPDATE projects SET stage=stage+1,updated_at=? WHERE id=?", (utc_now(), project_id))
                self._event(project_id, "PROJECT_ADVANCED", {"from": stage, "to": stage + 1})
        return self.project(project_id)

    def events(self, project_id):
        self._project_required(project_id)
        return [dict(r) for r in self.db.execute("SELECT * FROM events WHERE project_id=? ORDER BY id", (project_id,))]

    def report(self, project_id):
        p = self._project_required(project_id)
        return {
            "project": p,
            "tasks": self.tasks(project_id),
            "gates": self.gates(project_id),
            "evidence": [{**{k: v for k, v in e.items() if k != "source_path"}, "integrity": self.verify_evidence(e["id"])} for e in self.evidence_list(project_id)],
            "events": self.events(project_id),
            "notes": "Các quyết định phê duyệt được nhập bởi người vận hành; chưa có xác minh định danh người phê duyệt hoặc CI/CD bên ngoài.",
        }
