"""Loopback dashboard smoke test. No outbound network or external services."""
import json
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def test_read_only_local_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite"
            cli = [sys.executable, "-m", "factory_control", "--db", str(db)]
            for args in (
                ["init"],
                ["project", "add", "--id", "UI-001", "--name", "Dự án thử", "--owner", "operator"],
            ):
                subprocess.run(cli + args, cwd=ROOT, check=True, capture_output=True)
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            server = subprocess.Popen(
                cli + ["serve", "--port", str(port)], cwd=ROOT,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            try:
                base = f"http://127.0.0.1:{port}"
                for _ in range(40):
                    try:
                        with urllib.request.urlopen(base + "/api/health", timeout=1) as resp:
                            self.assertEqual(json.load(resp)["status"], "LOCAL_READ_ONLY")
                        break
                    except OSError:
                        if server.poll() is not None:
                            raise AssertionError("Dashboard process exited before HTTP ready")
                        time.sleep(.1)
                else:
                    self.fail("Dashboard did not start on loopback")
                with urllib.request.urlopen(base + "/api/projects", timeout=2) as resp:
                    self.assertEqual(json.load(resp)[0]["id"], "UI-001")
                    self.assertIn("default-src 'none'", resp.headers["Content-Security-Policy"])
                with urllib.request.urlopen(base + "/", timeout=2) as resp:
                    self.assertIn(b"<!doctype html>", resp.read())
                with self.assertRaises(urllib.error.HTTPError) as denied:
                    urllib.request.urlopen(urllib.request.Request(base + "/api/projects", method="POST"), timeout=2)
                self.assertEqual(denied.exception.code, 405)
                with self.assertRaises(urllib.error.HTTPError) as missing:
                    urllib.request.urlopen(base + "/private", timeout=2)
                self.assertEqual(missing.exception.code, 404)
            finally:
                server.terminate()
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
