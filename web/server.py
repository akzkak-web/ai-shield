from typing import List
"""
AI Shield - Web Server (FastAPI)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

from core.scanner import scanner
from core.config import t, DEFAULT_PORTS, I18N

app = FastAPI(title="AI Shield", version="1.0.0")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================================================
# API Models
# ============================================================
class ScanRequest(BaseModel):
    target: str
    ports: Optional[List[int]] = None
    checks: Optional[List[str]] = None
    lang: str = "zh"


# ============================================================
# API Routes
# ============================================================
@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main web UI."""
    html_path = static_dir / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.post("/api/scan")
async def start_scan(req: ScanRequest):
    """Start a new security scan."""
    target = req.target.strip()
    if not target:
        raise HTTPException(400, "Target is required")

    # Parse ports
    ports = req.ports or list(DEFAULT_PORTS.keys())

    # Parse checks
    checks = req.checks or None  # None = all checks

    try:
        result = await scanner.run_scan(target, ports, checks)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(500, f"Scan failed: {str(e)}")


@app.get("/api/history")
async def get_history():
    """Get scan history."""
    return JSONResponse(scanner.get_history())


@app.get("/api/scan/{scan_id}")
async def get_scan(scan_id: str):
    """Get a specific scan result."""
    result = scanner.get_scan(scan_id)
    if not result:
        raise HTTPException(404, "Scan not found")
    return JSONResponse(result)


@app.get("/api/i18n/{lang}")
async def get_i18n(lang: str):
    """Get translations."""
    if lang not in I18N:
        raise HTTPException(400, f"Language '{lang}' not supported")
    return JSONResponse(I18N[lang])


@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8899)
