"""Read-only loopback dashboard. No remote access and no mutation API."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
from . import __version__

STATIC = Path(__file__).parent / "static"


def make_handler(store):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, data: bytes, status=200, content_type="application/json; charset=utf-8"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            # An arbitrary Host could enable DNS rebinding against this
            # unauthenticated loopback service. Never accept external hosts.
            host = self.headers.get('Host', '').lower()
            if host not in ('127.0.0.1', 'localhost', '127.0.0.1:%d' % self.server.server_port,
                            'localhost:%d' % self.server.server_port):
                return self.reply(b'{"error":"INVALID_HOST"}', status=403)
            path = unquote(urlsplit(self.path).path)
            try:
                if path == "/api/health":
                    content = {"status": "LOCAL_READ_ONLY", "version": __version__}
                elif path == "/api/projects":
                    content = store.projects()
                elif path.startswith("/api/projects/"):
                    project_id = path.split("/")[-1]
                    content = store.report(project_id)
                elif path in ("/", "/index.html", "/app.js", "/style.css"):
                    name = "index.html" if path == "/" else path.lstrip("/")
                    mime = "text/html; charset=utf-8" if name.endswith("html") else "application/javascript; charset=utf-8" if name.endswith("js") else "text/css; charset=utf-8"
                    return self.reply((STATIC / name).read_bytes(), content_type=mime)
                else:
                    return self.reply(b'{"error":"NOT_FOUND"}', status=404)
                return self.reply(json.dumps(content, ensure_ascii=False).encode("utf-8"))
            except ValueError:
                return self.reply(b'{"error":"PROJECT_NOT_FOUND"}', status=404)

        def do_POST(self):
            return self.reply(b'{"error":"READ_ONLY"}', status=405)

        do_PUT = do_POST
        do_PATCH = do_POST
        do_DELETE = do_POST

        def log_message(self, *_):
            pass
    return Handler


def serve(store, port=8765):
    if not 1 <= port <= 65535:
        raise ValueError("Cổng phải nằm trong khoảng 1–65535")
    # Local-only by design; no authentication is provided, so NEVER bind publicly.
    with HTTPServer(("127.0.0.1", port), make_handler(store)) as server:
        print(f"Dashboard chỉ đọc: http://127.0.0.1:{port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
