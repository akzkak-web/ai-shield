from fastapi.testclient import TestClient
import pytest

import web.server as ws
from web.server import app


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch):
    monkeypatch.setattr(ws.settings, "access_token", "")
    monkeypatch.setattr(ws.settings, "cors_origins", [])
    monkeypatch.setattr(ws.settings, "allow_private", False)
    monkeypatch.setattr(ws.settings, "rate_limit_requests", 20)
    ws._rate_hits.clear()


def test_no_cors_by_default():
    client = TestClient(app)
    resp = client.get("/api/health", headers={"Origin": "https://evil.example.com"})
    assert "access-control-allow-origin" not in {k.lower() for k in resp.headers}


def test_auth_required_when_token_set(monkeypatch):
    monkeypatch.setattr(ws.settings, "access_token", "secret-token")
    client = TestClient(app)
    resp = client.post("/api/scan", json={"target": "127.0.0.1"})
    assert resp.status_code == 401


def test_auth_accepted_with_bearer(monkeypatch):
    monkeypatch.setattr(ws.settings, "access_token", "secret-token")
    async def fake_run_scan(target, ports, checks, allow_private=None):
        return {"id": "x", "grade": "A", "findings": []}
    monkeypatch.setattr(ws.scanner, "run_scan", fake_run_scan)
    client = TestClient(app)
    resp = client.post(
        "/api/scan",
        json={"target": "127.0.0.1"},
        headers={"Authorization": "Bearer secret-token"},
    )
    assert resp.status_code == 200


def test_public_target_rejected(monkeypatch):
    called = {"v": False}
    async def fake_run_scan(target, ports, checks, allow_private=None):
        called["v"] = True
        return {}
    monkeypatch.setattr(ws.scanner, "run_scan", fake_run_scan)
    client = TestClient(app)
    resp = client.post("/api/scan", json={"target": "8.8.8.8"})
    assert resp.status_code == 400
    assert called["v"] is False


def test_rate_limit(monkeypatch):
    monkeypatch.setattr(ws.settings, "rate_limit_requests", 1)
    async def fake_run_scan(target, ports, checks, allow_private=None):
        return {"id": "x", "grade": "A", "findings": []}
    monkeypatch.setattr(ws.scanner, "run_scan", fake_run_scan)
    client = TestClient(app)
    first = client.post("/api/scan", json={"target": "127.0.0.1"})
    second = client.post("/api/scan", json={"target": "127.0.0.1"})
    assert first.status_code == 200
    assert second.status_code == 429
