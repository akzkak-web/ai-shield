"""Tests for the commercial Quick Check product mode.

The quick check runs a fixed, read-only check set against Ollama. These
tests use an in-process mock Ollama on 127.0.0.1 and exercise the real CLI
path end to end.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from checks import QUICK_CHECK_NAMES


ROOT = Path(__file__).resolve().parent.parent


class _MockOllamaHandler(BaseHTTPRequestHandler):
    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/version":
            return self._json({"version": "0.1.33"})
        if self.path == "/api/tags":
            return self._json({"models": [{"name": "demo:latest"}]})
        if self.path == "/v1/models":
            return self._json({"object": "list", "data": [{"id": "demo:latest"}]})
        if self.path == "/":
            return self._json({"ok": True})
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):  # silence per-request logs
        pass


@pytest.fixture()
def mock_ollama():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _MockOllamaHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()


def _run_cli(*args, env=None):
    return subprocess.run(
        [sys.executable, "ai-shield.py", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )


def test_quick_check_names_are_read_only():
    assert set(QUICK_CHECK_NAMES) == {
        "network_exposure",
        "auth_missing",
        "cors_check",
        "model_access",
        "resource_abuse",
        "cve_check",
    }


def test_quick_check_requires_engagement(mock_ollama):
    proc = _run_cli("quick-check", "127.0.0.1", "--ports", str(mock_ollama))
    assert proc.returncode == 2


def test_quick_check_rejects_subnet():
    proc = _run_cli(
        "quick-check", "127.0.0.0/30",
        "--customer", "c", "--engagement-id", "E-1",
    )
    assert proc.returncode == 2


def test_quick_check_end_to_end_json(mock_ollama, tmp_path):
    out = tmp_path / "report.json"
    proc = _run_cli(
        "quick-check", "127.0.0.1",
        "--ports", str(mock_ollama),
        "--customer", "示例客户有限公司",
        "--engagement-id", "QC-2026-0001",
        "--authorized-scope", "127.0.0.1 本地演示目标",
        "-o", str(out),
    )
    # A confirmed critical finding trips the fail gate (exit 1) by design;
    # the JSON report is still written.
    assert proc.returncode in (0, 1), proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))

    assert data["assessment_type"] == "AI Shield Quick Check — Ollama"
    assert data["customer"] == "示例客户有限公司"
    assert data["engagement_id"] == "QC-2026-0001"
    assert data["authorized_scope"] == "127.0.0.1 本地演示目标"
    assert data["retest_status"] == "not_retested"
    assert data["tool_version"]

    services = data["port_data"]["services"]
    detected = [s for s in services if s.get("detected")]
    assert any(s["service"] == "Ollama" for s in detected)

    # Read-only check set only: no generation probes ran.
    assert set(data["check_results"]) == set(QUICK_CHECK_NAMES)
    assert "prompt_injection" not in data["check_results"]
    assert "data_leak" not in data["check_results"]

    # The mock exposes an unauthenticated model list: confirmed critical.
    assert data["check_results"]["auth_missing"] == "fail"
    assert data["summary"]["critical"] >= 1


def test_quick_check_pdf_contains_engagement_sections(mock_ollama, tmp_path):
    from core.report import generate_pdf_report

    out = tmp_path / "report.json"
    proc = _run_cli(
        "quick-check", "127.0.0.1",
        "--ports", str(mock_ollama),
        "--customer", "示例客户有限公司",
        "--engagement-id", "QC-2026-0002",
        "-o", str(out),
    )
    assert proc.returncode in (0, 1), proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))

    pdf_path = tmp_path / "report.pdf"
    generate_pdf_report(data, str(pdf_path))
    assert pdf_path.exists() and pdf_path.stat().st_size > 0

    if shutil.which("mutool") is None:
        pytest.skip("mutool not available for PDF text extraction")
    text = subprocess.run(
        ["mutool", "draw", "-F", "txt", str(pdf_path)],
        capture_output=True,
        text=True,
    ).stdout
    assert "示例客户有限公司" in text
    assert "QC-2026-0002" in text
    assert "复测状态" in text
    assert "AI Shield 版本" in text


def test_scan_traffic_ignores_ambient_proxy(mock_ollama, tmp_path):
    """A dead ambient proxy must not break loopback scans (trust_env=False)."""
    out = tmp_path / "report.json"
    env = {k: v for k, v in os.environ.items() if k.lower() != "no_proxy"}
    env.update({
        "HTTP_PROXY": "http://127.0.0.1:9",
        "HTTPS_PROXY": "http://127.0.0.1:9",
        "ALL_PROXY": "http://127.0.0.1:9",
    })
    proc = _run_cli(
        "quick-check", "127.0.0.1",
        "--ports", str(mock_ollama),
        "--customer", "c",
        "--engagement-id", "E-2",
        "-o", str(out),
        env=env,
    )
    assert proc.returncode in (0, 1), proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    detected = [s for s in data["port_data"]["services"] if s.get("detected")]
    assert any(s["service"] == "Ollama" for s in detected)
