"""
Scan baseline and diff comparison.

A baseline is a versioned, sanitized snapshot of one scan's findings. Diffing
produces ``new`` / ``fixed`` / ``persistent`` / ``changed`` / ``unknown``
entries. A baseline finding is only marked ``fixed`` when the same check ran
again with a definitive ``pass`` -- never merely because the finding is absent
or the target became unreachable.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from core.rating import SEVERITY_ORDER


SCANNER_VERSION = "0.1.0-rc.1"
BASELINE_SCHEMA_VERSION = 2


class BaselineError(Exception):
    """Raised when a baseline is missing, corrupt, unsupported, or mismatched."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fingerprint(finding: dict) -> str:
    """Stable finding identity: check_id + service + port.

    Evidence text, timestamps, request ids and severity/confidence are
    intentionally excluded so that cosmetic evidence changes do not look like
    new findings, while a severity/confidence change is detected separately.
    """
    key = "|".join(
        [
            str(finding.get("check_id", "")),
            str(finding.get("service", "")),
            str(finding.get("port", "")),
        ]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


_SECRET_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"(?i)(token|api[-_]?key|authorization|password|secret)\s*[:=]\s*[^,;\n]*"),
]


def sanitize_evidence(text: object, limit: int = 200) -> str:
    out = str(text or "")
    for pattern in _SECRET_PATTERNS:
        out = pattern.sub("***", out)
    return out[:limit]


def build_baseline(result: dict) -> dict:
    findings = []
    for f in result.get("findings", []):
        findings.append(
            {
                "fingerprint": fingerprint(f),
                "check_id": f.get("check_id", ""),
                "check_name": f.get("check_name", ""),
                "severity": f.get("severity", "info"),
                "confidence": f.get("confidence", ""),
                "status": "finding",
                "service": f.get("service", ""),
                "port": f.get("port", 0),
                "evidence_summary": sanitize_evidence(f.get("evidence", "")),
            }
        )
    return {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "scanner_version": SCANNER_VERSION,
        "created_at": _now(),
        "target": result.get("target", ""),
        "coverage_status": result.get("coverage_status", "none"),
        "grade": result.get("grade", "N/A"),
        "findings": findings,
    }


def save_baseline(baseline: dict, path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(baseline, ensure_ascii=False, indent=2)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".baseline-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return p


def load_baseline(path) -> dict:
    p = Path(path)
    if not p.exists():
        raise BaselineError(f"baseline file not found: {p}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineError(f"baseline is corrupt or not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise BaselineError("baseline root must be an object")
    if raw.get("schema_version") != BASELINE_SCHEMA_VERSION:
        raise BaselineError(
            f"unsupported baseline schema_version: {raw.get('schema_version')}"
        )
    if not isinstance(raw.get("target"), str) or not raw.get("target"):
        raise BaselineError("baseline is missing a valid 'target'")
    if not isinstance(raw.get("findings"), list):
        raise BaselineError("baseline 'findings' must be a list")
    return raw


def _entry(status: str, f: dict, old: Optional[dict] = None, reason: str = "") -> dict:
    e = {
        "status": status,
        "fingerprint": f.get("fingerprint") or fingerprint(f),
        "check_id": f.get("check_id", ""),
        "check_name": f.get("check_name", ""),
        "severity": f.get("severity", "info"),
        "confidence": f.get("confidence", ""),
        "service": f.get("service", ""),
        "port": f.get("port", 0),
    }
    if status == "changed" and old is not None:
        e["previous_severity"] = old.get("severity", "info")
        e["previous_confidence"] = old.get("confidence", "")
        e["reason"] = (
            f"severity/confidence changed: "
            f"{old.get('severity')}/{old.get('confidence')} -> "
            f"{f.get('severity')}/{f.get('confidence')}"
        )
    if reason:
        e["reason"] = reason
    return e


def compare_baseline(baseline: dict, current: dict) -> dict:
    if baseline.get("target") != current.get("target"):
        raise BaselineError(
            f"target mismatch: baseline={baseline.get('target')} current={current.get('target')}"
        )
    version_note = None
    if baseline.get("scanner_version") != SCANNER_VERSION:
        version_note = (
            f"scanner version changed ({baseline.get('scanner_version')} -> "
            f"{SCANNER_VERSION}); comparison may be unreliable"
        )

    base = {f["fingerprint"]: f for f in baseline.get("findings", [])}
    cur = {fingerprint(f): f for f in current.get("findings", [])}
    cur_results = current.get("check_results", {})

    entries: List[dict] = []
    for fp, b in base.items():
        if fp in cur:
            c = cur[fp]
            changed = (b.get("severity") != c.get("severity")) or (
                b.get("confidence") != c.get("confidence")
            )
            entries.append(_entry("changed" if changed else "persistent", c, old=b))
        else:
            check_name = b.get("check_name", "")
            status = cur_results.get(check_name)
            if status == "pass":
                entries.append(
                    _entry("fixed", b, reason=f"check '{check_name}' passed in current scan")
                )
            else:
                entries.append(
                    _entry(
                        "unknown",
                        b,
                        reason=(
                            f"not fixed: check '{check_name}' status="
                            f"{status or 'not-run'}"
                        ),
                    )
                )

    for fp, c in cur.items():
        if fp not in base:
            entries.append(_entry("new", c))

    summary = {}
    for e in entries:
        summary[e["status"]] = summary.get(e["status"], 0) + 1

    return {
        "target": baseline.get("target"),
        "scanner_version": SCANNER_VERSION,
        "version_note": version_note,
        "entries": entries,
        "summary": summary,
    }


def new_confirmed_above(entries: List[dict], threshold: str) -> List[dict]:
    rank = SEVERITY_ORDER.get(threshold)
    if rank is None:
        raise ValueError(f"invalid fail-on-new threshold: {threshold}")
    out = []
    for e in entries:
        if e.get("status") != "new":
            continue
        if e.get("confidence") != "confirmed":
            continue
        if SEVERITY_ORDER.get(e.get("severity", "info"), 0) >= rank:
            out.append(e)
    return out


__all__ = [
    "SCANNER_VERSION",
    "BaselineError",
    "fingerprint",
    "sanitize_evidence",
    "build_baseline",
    "save_baseline",
    "load_baseline",
    "compare_baseline",
    "new_confirmed_above",
]
