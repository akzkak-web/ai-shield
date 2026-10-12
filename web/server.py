"""
AI Shield - Web server (FastAPI).

Security posture is default-deny:

* CORS is disabled unless ``AI_SHIELD_CORS_ORIGINS`` is set.
* When ``AI_SHIELD_ACCESS_TOKEN`` is set, sensitive endpoints require a
  bearer token (constant-time comparison).
* Scan targets are validated against :mod:`core.target_policy` so the API
  cannot be used as an SSRF / internal-port-scan primitive.
* Request body size, target count, concurrency and request rate are bounded.
* Errors do not leak stack traces or internal state.
"""
from __future__ import annotations

import asyncio
import hmac
import ipaddress
import logging
import os
import sys
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core.config import DEFAULT_PORTS, I18N, settings, t
from core.scanner import scanner
from core.target_policy import TargetPolicyError, validate_target


logger = logging.getLogger("ai-shield.web")

app = FastAPI(title="AI Shield", version="1.1.0")


def assert_safe_bind(host: str) -> None:
    """Refuse to bind to a non-loopback address without authentication."""
    try:
        is_loopback = ipaddress.ip_address(host).is_loopback
    except ValueError:
        is_loopback = False
    if not is_loopback and not settings.access_token:
        raise RuntimeError(
            "refusing to bind to a non-loopback address without "
            "AI_SHIELD_ACCESS_TOKEN; set an access token or bind to 127.0.0.1"
        )


class BodySizeLimitMiddleware:
    """Reject request bodies larger than ``max_bytes`` (including chunked)."""

    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Fast path: reject via Content-Length before reading the body.
        headers = {k.decode("latin-1"): v.decode("latin-1") for k, v in scope.get("headers", [])}
        content_length = headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > self.max_bytes:
            response = JSONResponse({"detail": "request body too large"}, status_code=413)
            await response(scope, receive, send)
            return

        # Buffer the body to enforce the limit for chunked/unknown length.
        chunks = []
        total = 0
        while True:
            message = await receive()
            if message["type"] != "http.request":
                break
            chunk = message.get("body", b"")
            chunks.append(chunk)
            total += len(chunk)
            if total > self.max_bytes:
                response = JSONResponse({"detail": "request body too large"}, status_code=413)
                await response(scope, receive, send)
                return
            if not message.get("more_body", False):
                break

        body = b"".join(chunks)
        sent = [False]

        async def replay_receive():
            if not sent[0]:
                sent[0] = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        await self.app(scope, replay_receive, send)


app.add_middleware(BodySizeLimitMiddleware, max_bytes=settings.max_body_bytes)

# CORS is opt-in. No origins -> no cross-origin access.
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )


static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


_rate_hits: Dict[str, deque] = defaultdict(deque)
_scan_lock = asyncio.Lock()


class ScanRequest(BaseModel):
    target: str = Field(..., max_length=255)
    ports: Optional[List[int]] = Field(default=None, max_length=settings.max_targets)
    checks: Optional[List[str]] = Field(default=None, max_length=64)
    lang: str = "zh"


def _authenticate(request: Request) -> None:
    if not settings.access_token:
        return
    provided = request.headers.get("Authorization") or request.headers.get("X-API-Token") or ""
    if provided.startswith("Bearer "):
        provided = provided[len("Bearer "):]
    if not hmac.compare_digest(provided, settings.access_token):
        raise HTTPException(401, "unauthorized")


def _rate_limit(request: Request) -> None:
    now = time.monotonic()
    client = request.client.host if request.client else "unknown"
    q = _rate_hits[client]
    while q and now - q[0] > settings.rate_limit_window_seconds:
        q.popleft()
    if len(q) >= settings.rate_limit_requests:
        raise HTTPException(429, "too many requests")
    q.append(now)


def _body_size(request: Request) -> None:
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > settings.max_body_bytes:
        raise HTTPException(413, "request body too large")


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = static_dir / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.1.0"}


@app.get("/api/i18n/{lang}")
async def get_i18n(lang: str):
    if lang not in I18N:
        raise HTTPException(400, "unsupported language")
    return JSONResponse(I18N[lang])


@app.get("/api/history", dependencies=[Depends(_authenticate)])
async def get_history():
    return JSONResponse(scanner.get_history())


@app.get("/api/scan/{scan_id}", dependencies=[Depends(_authenticate)])
async def get_scan(scan_id: str):
    result = scanner.get_scan(scan_id)
    if not result:
        raise HTTPException(404, "scan not found")
    return JSONResponse(result)


@app.post(
    "/api/scan",
    dependencies=[Depends(_authenticate), Depends(_rate_limit), Depends(_body_size)],
)
async def start_scan(req: ScanRequest):
    target = req.target.strip()
    if not target:
        raise HTTPException(400, "target is required")

    # Enforce the target policy before any network activity.
    decision = validate_target(
        target,
        allow_private=settings.allow_private,
        allowed_targets=settings.allowed_targets,
    )
    if not decision.allowed:
        raise HTTPException(400, f"target rejected: {decision.reason}")

    ports = req.ports or list(DEFAULT_PORTS.keys())
    ports = [p for p in ports if isinstance(p, int) and 1 <= p <= 65535]
    if len(ports) > settings.max_targets:
        raise HTTPException(400, "too many ports")

    checks = req.checks or None

    try:
        async with _scan_lock:
            result = await asyncio.wait_for(
                scanner.run_scan(
                    target,
                    ports,
                    checks,
                    allow_private=settings.allow_private,
                ),
                timeout=settings.scan_timeout_seconds,
            )
    except asyncio.TimeoutError:
        raise HTTPException(504, "scan timed out")
    except (ValueError, TargetPolicyError) as exc:
        raise HTTPException(400, f"target rejected: {exc}")
    except Exception as exc:
        logger.exception("scan failed")
        raise HTTPException(500, "scan failed")

    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn

    assert_safe_bind(settings.host)
    uvicorn.run(app, host=settings.host, port=settings.port)
