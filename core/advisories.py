"""
Unified vulnerability advisory model, local cache and matching.

An advisory is a merged record whose base comes from NVD and may be enriched
with EPSS and CISA KEV. Missing data is represented as ``None`` or an empty
collection -- never a fabricated default.

``kev_listed`` is a tri-state: ``True`` (listed in a verified KEV snapshot),
``False`` (verified absent from that snapshot) and ``None`` (unknown because
no verified snapshot was retrieved). A failed KEV query therefore does not
mark a CVE as "not exploited".

The on-disk cache is written atomically (temp file + rename) so an interrupted
download never corrupts an existing good cache.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from core.versioning import parse_version, version_in_ranges


_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "advisories.json"

_CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,}$")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_cve_id(cve_id: str) -> bool:
    return bool(_CVE_RE.match(cve_id or ""))


def cvss_to_severity(score: Optional[float]) -> str:
    if score is None:
        return "info"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    if score >= 0.1:
        return "low"
    return "info"


@dataclass(frozen=True)
class Advisory:
    cve_id: str
    source: str
    summary: str = ""
    affected_products: Tuple[str, ...] = ()
    affected_versions: Tuple[str, ...] = ()
    cvss_score: Optional[float] = None
    cvss_version: Optional[str] = None
    epss_score: Optional[float] = None
    epss_percentile: Optional[float] = None
    kev_listed: Optional[bool] = None
    published_at: str = ""
    modified_at: str = ""
    retrieved_at: str = ""
    source_url: str = ""
    source_record_id: str = ""
    fixed: Optional[str] = None
    severity: str = "high"

    # Backward-compatible aliases.
    @property
    def id(self) -> str:
        return self.cve_id

    @property
    def affected(self) -> Tuple[str, ...]:
        return self.affected_versions

    @property
    def url(self) -> str:
        return self.source_url

    def to_dict(self) -> dict:
        return {
            "cve_id": self.cve_id,
            "source": self.source,
            "summary": self.summary,
            "affected_products": list(self.affected_products),
            "affected_versions": list(self.affected_versions),
            "cvss_score": self.cvss_score,
            "cvss_version": self.cvss_version,
            "epss_score": self.epss_score,
            "epss_percentile": self.epss_percentile,
            "kev_listed": self.kev_listed,
            "published_at": self.published_at,
            "modified_at": self.modified_at,
            "retrieved_at": self.retrieved_at,
            "source_url": self.source_url,
            "source_record_id": self.source_record_id,
            "fixed": self.fixed,
            "severity": self.severity,
        }


def _as_str(value) -> str:
    return "" if value is None else str(value)


def _as_float(value, lo: Optional[float] = None, hi: Optional[float] = None) -> Optional[float]:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if lo is not None and f < lo:
        return None
    if hi is not None and f > hi:
        return None
    return f


def _as_tri_bool(value) -> Optional[bool]:
    # Only a real bool is accepted; everything else is unknown (None).
    return value if isinstance(value, bool) else None


def _as_tuple(value) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(x) for x in value if x is not None and str(x) != "")
    return (str(value),)


def _coerce_advisory(item: dict) -> Optional[Advisory]:
    cve_id = _as_str(item.get("cve_id") or item.get("id")).strip()
    if not validate_cve_id(cve_id):
        return None
    source = _as_str(item.get("source")).strip().lower()
    if not source:
        return None

    cvss = _as_float(item.get("cvss_score"), 0.0, 10.0)
    epss = _as_float(item.get("epss_score"), 0.0, 1.0)
    pct = _as_float(item.get("epss_percentile"), 0.0, 1.0)
    kev = _as_tri_bool(item.get("kev_listed"))

    fixed = item.get("fixed")
    fixed = str(fixed) if fixed not in (None, "") else None
    severity = _as_str(item.get("severity")).strip().lower() or cvss_to_severity(cvss)

    return Advisory(
        cve_id=cve_id,
        source=source,
        summary=_as_str(item.get("summary")),
        affected_products=_as_tuple(item.get("affected_products")),
        affected_versions=_as_tuple(item.get("affected_versions")),
        cvss_score=cvss,
        cvss_version=_as_str(item.get("cvss_version")).strip() or None,
        epss_score=epss,
        epss_percentile=pct,
        kev_listed=kev,
        published_at=_as_str(item.get("published_at")),
        modified_at=_as_str(item.get("modified_at")),
        retrieved_at=_as_str(item.get("retrieved_at")),
        source_url=_as_str(item.get("source_url") or item.get("url")),
        source_record_id=_as_str(item.get("source_record_id")),
        fixed=fixed,
        severity=severity,
    )


def load_advisories(path: Optional[Path] = None) -> List[Advisory]:
    p = Path(path) if path else _DATA_FILE
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out: List[Advisory] = []
    for item in raw.get("advisories", []):
        adv = _coerce_advisory(item)
        if adv is not None:
            out.append(adv)
    return out


def load_cache_meta(path: Optional[Path] = None) -> dict:
    p = Path(path) if path else _DATA_FILE
    if not p.exists():
        return {"available": False, "retrieved_at": "", "sources": {}}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"available": False, "retrieved_at": "", "sources": {}}
    return {
        "available": True,
        "retrieved_at": raw.get("retrieved_at") or raw.get("generated_at") or "",
        "sources": raw.get("sources", {}),
    }


def save_advisories(advisories, sources_status: dict, path: Optional[Path] = None) -> Path:
    p = Path(path) if path else _DATA_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 2,
        "generated_at": now_utc(),
        "retrieved_at": now_utc(),
        "sources": sources_status,
        "advisories": [a.to_dict() for a in advisories],
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".advisories-", suffix=".tmp")
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


def cache_status(ttl_seconds: int, path: Optional[Path] = None) -> str:
    """Return ``fresh``, ``stale`` or ``unavailable``."""
    meta = load_cache_meta(path)
    if not meta["available"]:
        return "unavailable"
    retrieved = meta.get("retrieved_at", "")
    if not retrieved:
        return "stale"
    try:
        dt = datetime.fromisoformat(retrieved.replace("Z", "+00:00"))
    except ValueError:
        return "stale"
    age = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()
    return "fresh" if (age >= 0 and age <= ttl_seconds) else "stale"


def advisory_database_available(path: Optional[Path] = None) -> bool:
    return bool(load_advisories(path))


def _product_matches(product: str, service: str) -> bool:
    a = (product or "").lower().strip()
    s = (service or "").lower()
    if not a:
        return False
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9])", s))


def _service_matches(advisory: Advisory, service: str) -> bool:
    return any(_product_matches(p, service) for p in advisory.affected_products)


def match_advisories(
    service: str,
    version: Optional[str],
    path: Optional[Path] = None,
) -> List[Tuple[Advisory, str]]:
    """Return ``(advisory, status)`` where status is affected/not_affected/unknown."""
    parsed = parse_version(version)
    results: List[Tuple[Advisory, str]] = []
    for adv in load_advisories(path):
        if not _service_matches(adv, service):
            continue
        if not adv.affected_versions or parsed is None:
            results.append((adv, "unknown"))
            continue
        in_range = version_in_ranges(parsed, adv.affected_versions)
        if in_range is True:
            results.append((adv, "affected"))
        elif in_range is False:
            results.append((adv, "not_affected"))
        else:
            results.append((adv, "unknown"))
    return results


__all__ = [
    "Advisory",
    "cvss_to_severity",
    "validate_cve_id",
    "now_utc",
    "load_advisories",
    "load_cache_meta",
    "save_advisories",
    "cache_status",
    "advisory_database_available",
    "match_advisories",
]
