"""
Orchestrates vulnerability-intelligence refresh and caching.

This is the *only* place that performs network fetches for advisories, and it
is never invoked by a normal local scan -- only when the user explicitly
triggers ``refresh-intel``.

The base advisory set comes from NVD. EPSS and KEV are enrichment layers:
when they fail, the base record remains valid and their fields are ``None``.
``kev_listed`` is set to ``False`` only when a verified KEV snapshot was
retrieved and the CVE was absent from it.
"""
from __future__ import annotations

from typing import Dict, Optional

from core.advisories import Advisory, cvss_to_severity, now_utc, save_advisories
from core.sources import EpssSource, KevSource, NvdSource


async def refresh_advisories(
    nvd_api_key: str = "",
    base_urls: Optional[Dict[str, str]] = None,
    client=None,
    path=None,
) -> dict:
    base_urls = base_urls or {}
    nvd_kwargs = {"api_key": nvd_api_key}
    if base_urls.get("nvd"):
        nvd_kwargs["base_url"] = base_urls["nvd"]
    epss_kwargs = {"base_url": base_urls["epss"]} if base_urls.get("epss") else {}
    kev_kwargs = {"base_url": base_urls["kev"]} if base_urls.get("kev") else {}
    nvd = NvdSource(**nvd_kwargs)
    epss = EpssSource(**epss_kwargs)
    kev = KevSource(**kev_kwargs)

    sources_status: Dict[str, dict] = {}

    nvd_records = []
    try:
        nvd_records, _ = await nvd.fetch(client=client)
        sources_status["nvd"] = {"status": "ok", "count": len(nvd_records), "retrieved_at": now_utc()}
    except Exception as exc:
        sources_status["nvd"] = {"status": "failed", "error": type(exc).__name__}

    epss_map: Dict[str, dict] = {}
    try:
        epss_map, _ = await epss.fetch(client=client)
        sources_status["epss"] = {"status": "ok", "count": len(epss_map), "retrieved_at": now_utc()}
    except Exception as exc:
        sources_status["epss"] = {"status": "failed", "error": type(exc).__name__}

    kev_map: Dict[str, dict] = {}
    kev_ok = False
    try:
        kev_map, _ = await kev.fetch(client=client)
        kev_ok = True
        sources_status["cisa_kev"] = {"status": "ok", "count": len(kev_map), "retrieved_at": now_utc()}
    except Exception as exc:
        sources_status["cisa_kev"] = {"status": "failed", "error": type(exc).__name__}

    if not nvd_records:
        # NVD is the base source; do not overwrite an existing good cache.
        return {
            "saved": False,
            "path": None,
            "count": 0,
            "reason": "NVD fetch failed; existing cache preserved",
            "sources": sources_status,
        }

    advisories = []
    for rec in nvd_records:
        cve = rec["cve_id"]
        epss_info = epss_map.get(cve, {})
        if kev_ok:
            kev_listed = cve in kev_map
        else:
            kev_listed = None
        advisories.append(
            Advisory(
                cve_id=rec["cve_id"],
                source="nvd",
                summary=rec.get("summary", ""),
                affected_products=tuple(rec.get("affected_products", [])),
                affected_versions=tuple(rec.get("affected_versions", [])),
                cvss_score=rec.get("cvss_score"),
                cvss_version=rec.get("cvss_version"),
                epss_score=epss_info.get("score"),
                epss_percentile=epss_info.get("percentile"),
                kev_listed=kev_listed,
                published_at=rec.get("published_at", ""),
                modified_at=rec.get("modified_at", ""),
                retrieved_at=now_utc(),
                source_url=rec.get("source_url", ""),
                source_record_id=rec.get("source_record_id", ""),
                severity=rec.get("severity") or cvss_to_severity(rec.get("cvss_score")),
            )
        )

    saved_path = save_advisories(advisories, sources_status, path)
    return {
        "saved": True,
        "path": str(saved_path),
        "count": len(advisories),
        "sources": sources_status,
    }


__all__ = ["refresh_advisories"]
