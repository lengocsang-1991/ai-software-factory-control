"""Command-line interface for the local AI Software Factory control plane."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from . import __version__
from .store import FactoryStore, PRIORITIES, STATUSES, GATE_KINDS
from .automation import AutomationEngine, RECIPES, SimulationProvider

DEFAULT_DB = Path(__file__).resolve().parents[1] / ".factory-state" / "factory.db"


def parser():
    p = argparse.ArgumentParser(prog="factory-control", description="AI Software Factory — quản trị cục bộ (không triển khai tự động)")
    p.add_argument("--db", default=str(DEFAULT_DB), help="Đường dẫn SQLite; mặc định .factory-state/factory.db")
    p.add_argument("--version", action="version", version=f"factory-control {__version__}")
    cmds = p.add_subparsers(dest="command", required=True)
    cmds.add_parser("init", help="Khởi tạo SQLite local")
    pj = cmds.add_parser("project", help="Quản trị dự án")
    sp = pj.add_subparsers(dest="operation", required=True)
    add = sp.add_parser("add")
    add.add_argument("--id", required=True); add.add_argument("--name", required=True)
    add.add_argument("--owner", required=True); add.add_argument("--description", default="")
    add.add_argument("--repository")
    sp.add_parser("list")
    show = sp.add_parser("show"); show.add_argument("--id", required=True)
    advance = sp.add_parser("advance"); advance.add_argument("--id", required=True)

    t = cmds.add_parser("task", help="Quản trị nhiệm vụ")
    st = t.add_subparsers(dest="operation", required=True)
    add = st.add_parser("add"); add.add_argument("--id", required=True)
    add.add_argument("--project", required=True); add.add_argument("--title", required=True)
    add.add_argument("--owner", required=True); add.add_argument("--description", default="")
    add.add_argument("--priority", default="NORMAL", choices=PRIORITIES)
    li = st.add_parser("list"); li.add_argument("--project", required=True)
    change = st.add_parser("status"); change.add_argument("--id", required=True)
    change.add_argument("--set", required=True, choices=STATUSES)
    change.add_argument("--evidence-id", type=int)

    e = cmds.add_parser("evidence", help="Ghi nhận và xác minh tệp bằng chứng")
    se = e.add_subparsers(dest="operation", required=True)
    add = se.add_parser("add"); add.add_argument("--project", required=True)
    add.add_argument("--type", required=True, choices=(*GATE_KINDS, "OTHER"))
    add.add_argument("--file", required=True)
    add.add_argument("--task"); add.add_argument("--note", default="")
    li = se.add_parser("list"); li.add_argument("--project", required=True)
    verify = se.add_parser("verify"); verify.add_argument("--id", required=True, type=int)

    g = cmds.add_parser("gate", help="Phê duyệt từng cổng chất lượng")
    sg = g.add_subparsers(dest="operation", required=True)
    li = sg.add_parser("list"); li.add_argument("--project", required=True)
    decide = sg.add_parser("decide"); decide.add_argument("--project", required=True)
    decide.add_argument("--number", type=int, required=True, choices=range(1, 9))
    decide.add_argument("--decision", required=True, choices=("APPROVED", "REJECTED"))
    decide.add_argument("--approver", required=True)
    decide.add_argument("--evidence-id", required=True, type=int)
    decide.add_argument("--note", default="")

    r = cmds.add_parser("report", help="Xuất báo cáo JSON")
    r.add_argument("--project", required=True)
    serve = cmds.add_parser("serve", help="Bảng điều khiển READ-ONLY tại 127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    auto = cmds.add_parser("automation", help="Điều phối Agent theo quy trình, chờ phê duyệt (không sửa mã)")
    sa = auto.add_subparsers(dest="operation", required=True)
    enqueue = sa.add_parser("enqueue")
    enqueue.add_argument("--project", required=True)
    enqueue.add_argument("--objective", required=True)
    enqueue.add_argument("--recipe", default="discovery", choices=sorted(RECIPES))
    enqueue.add_argument("--provider", default="simulation", choices=("simulation", "openai"))
    enqueue.add_argument("--task-id")
    li = sa.add_parser("list"); li.add_argument("--project", required=True)
    sh = sa.add_parser("show"); sh.add_argument("--run", required=True)
    manifest = sa.add_parser("manifest"); manifest.add_argument("--run", required=True)
    retry = sa.add_parser("retry"); retry.add_argument("--run", required=True)
    intake = sa.add_parser("intake", help="Chỉ đọc issue factory:ready do chủ repo tạo; nhập vào SQLite local")
    intake.add_argument("--project", required=True)
    intake.add_argument("--enqueue", action="store_true", help="Đưa issue vào hàng đợi Agent theo discovery")
    intake.add_argument("--provider", default="simulation", choices=("simulation", "openai"))
    decide = sa.add_parser("decide"); decide.add_argument("--run", required=True)
    decide.add_argument("--decision", choices=("APPROVED", "REJECTED"), required=True)
    decide.add_argument("--actor", required=True); decide.add_argument("--note", default="")

    worker = cmds.add_parser("worker", help="Thực thi tuần tự các Agent; mặc định chỉ mô phỏng")
    worker.add_argument("--provider", default="simulation", choices=("simulation", "openai"))
    worker.add_argument("--confirm-cost", action="store_true", help="Bắt buộc khi dùng API OpenAI tính phí")
    worker.add_argument("--loop", action="store_true", help="Worker chạy liên tục ở máy chủ riêng")
    worker.add_argument("--interval", type=int, default=30, help="Giây giữa các lần kiểm tra, 2-3600")
    return p


def dispatch(store: FactoryStore, args):
    cmd, op = args.command, getattr(args, "operation", "")
    if cmd == "init":
        return {"status": "READY_LOCAL", "db": str(store.path), "version": __version__}
    if cmd == "project":
        if op == "add": return store.add_project(args.id, args.name, args.owner, args.description, args.repository)
        if op == "list": return store.projects()
        if op == "show": return store.report(args.id)
        if op == "advance": return store.advance(args.id)
    if cmd == "task":
        if op == "add": return store.add_task(args.id, args.project, args.title, args.owner, args.priority, args.description)
        if op == "list": return store.tasks(args.project)
        if op == "status": return store.change_task_status(args.id, args.set, args.evidence_id)
    if cmd == "evidence":
        if op == "add": return store.add_evidence(args.project, args.type, args.file, args.note, args.task)
        if op == "list": return [{k: v for k, v in e.items() if k != "source_path"} for e in store.evidence_list(args.project)]
        if op == "verify": return store.verify_evidence(args.id)
    if cmd == "gate":
        if op == "list": return store.gates(args.project)
        if op == "decide": return store.decide_gate(args.project, args.number, args.decision, args.approver, args.evidence_id, args.note)
    if cmd == "automation":
        engine = AutomationEngine(store)
        if op == "enqueue": return engine.create(args.project, args.objective, args.recipe, args.provider, args.task_id)
        if op == "list": return engine.list(args.project)
        if op == "show": return engine.get(args.run)
        if op == "manifest": return engine.output_manifest(args.run)
        if op == "retry": return engine.retry(args.run)
        if op == "intake":
            from .github_intake import ingest
            return ingest(store, args.project, enqueue=args.enqueue, provider=args.provider)
        if op == "decide": return engine.decide(args.run, args.decision, args.actor, args.note)
    if cmd == "worker":
        import time
        if not 2 <= args.interval <= 3600:
            raise ValueError("Interval phải từ 2 đến 3600 giây")
        if args.provider == "openai":
            if not args.confirm_cost:
                raise ValueError("Worker OpenAI cần --confirm-cost (lời gọi API có thể phát sinh chi phí)")
            from .providers import OpenAITextProvider
            provider = OpenAITextProvider()
        else:
            provider = SimulationProvider()
        engine = AutomationEngine(store)
        if not args.loop:
            return engine.run_one(args.provider, provider) or {"status": "NO_QUEUED_RUN"}
        try:
            while True:
                engine.run_one(args.provider, provider)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            return {"status": "WORKER_STOPPED"}
    if cmd == "report": return store.report(args.project)
    if cmd == "serve":
        from .web import serve
        return serve(store, args.port)
    raise ValueError("Lệnh không được hỗ trợ")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        with FactoryStore(args.db) as store:
            result = dispatch(store, args)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, RuntimeError, sqlite3.IntegrityError, OSError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
