"""Real-service integration tests against a Dockerized Ollama.

No model is pulled: the tests rely on endpoints that do not require model
inference (``/api/version``, ``/api/tags``, ``/v1/models``). An empty model
list is itself a meaningful case to verify -- the scanner must NOT treat it
as a confirmed vulnerability, and must NOT interpret a missing service as
"secure".
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import httpx
import pytest


ROOT = Path(__file__).resolve().parent.parent.parent

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(shutil.which("docker") is None, reason="docker not available"),
]


def _run_scan(port: int, *extra: str):
    return subprocess.run(
        [sys.executable, "ai-shield.py", "scan", "127.0.0.1", "--ports", str(port), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_ollama_version_and_tags(ollama):
    with httpx.Client(base_url=f"http://{ollama['host']}:{ollama['port']}", timeout=10) as c:
        version = c.get("/api/version")
        assert version.status_code == 200
        assert "version" in version.json()
        tags = c.get("/api/tags")
        assert tags.status_code == 200
        assert "models" in tags.json()


def test_service_discovery_and_json_report(ollama, tmp_path):
    out = tmp_path / "report.json"
    proc = _run_scan(ollama["port"], "-o", str(out))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    services = data.get("port_data", {}).get("services", [])
    detected = [s for s in services if s.get("detected")]
    assert detected, "Ollama was not detected"
    assert any(s["service"] == "Ollama" for s in detected)


def test_semantics_with_no_models(ollama, tmp_path):
    """No model pulled: auth/model-access must be unknown, not a confirmed vuln."""
    out = tmp_path / "report.json"
    proc = _run_scan(ollama["port"], "-o", str(out))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    cr = data.get("check_results", {})
    # Loopback target -> network exposure passes.
    assert cr.get("network_exposure") == "pass"
    # Empty model list: cannot confirm missing auth / model listing.
    assert cr.get("auth_missing") in ("unknown", "pass")
    assert cr.get("model_access") in ("unknown", "pass")
    # No confirmed findings must exist without model evidence.
    assert data.get("summary", {}).get("critical", 0) == 0


def test_baseline_and_diff_roundtrip(ollama, tmp_path):
    bl = tmp_path / "baseline.json"
    proc = _run_scan(ollama["port"], "--baseline-out", str(bl))
    assert proc.returncode == 0, proc.stderr
    assert bl.exists()

    diff = tmp_path / "diff.json"
    proc2 = _run_scan(ollama["port"], "--baseline", str(bl), "--diff-json", str(diff))
    assert proc2.returncode == 0, proc2.stderr
    data = json.loads(diff.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "entries" in data
