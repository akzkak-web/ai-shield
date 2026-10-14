"""
Adapters for the NVD, FIRST EPSS and CISA KEV public data sources.

Each adapter only parses what the source actually provides. Missing or
unparseable fields are dropped/omitted rather than guessed. EPSS and KEV are
enrichment data: their presence never proves a target is vulnerable.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import httpx

from core.advisories import validate_cve_id


class SourceError(Exception):
    """Raised when a source cannot be queried successfully."""


class NvdSource:
    name = "nvd"

    def __init__(
        self,
        base_url: str = "https://services.nvd.nist.gov/rest/json/cves/2.0",
        api_key: str = "",
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    async def fetch(
        self,
        client: Optional[httpx.AsyncClient] = None,
        results_per_page: int = 2000,
    ) -> Tuple[List[dict], dict]:
        records: List[dict] = []
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["apiKey"] = self.api_key
        own = client is None
        if own:
            client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=False)
        start_index = 0
        try:
            while True:
                url = f"{self.base_url}?startIndex={start_index}&resultsPerPage={results_per_page}"
                resp = await client.get(url, headers=headers)
                if resp.status_code == 429:
                    raise SourceError("NVD rate limited (HTTP 429)")
                if resp.status_code >= 500:
                    raise SourceError(f"NVD server error (HTTP {resp.status_code})")
                resp.raise_for_status()
                data = resp.json()
                for v in data.get("vulnerabilities", []):
                    rec = self._parse(v.get("cve", {}))
                    if rec is not None:
                        records.append(rec)
                total = int(data.get("totalResults", 0))
                start_index += int(data.get("resultsPerPage", results_per_page))
                if start_index >= total:
                    break
        finally:
            if own:
                await client.aclose()
        return records, {"status": "ok", "count": len(records)}

    def _parse(self, cve: dict) -> Optional[dict]:
        cve_id = cve.get("id")
        if not validate_cve_id(cve_id):
            return None
        summary = ""
        for d in cve.get("descriptions", []):
            if d.get("lang") == "en":
                summary = d.get("value", "")
                break
        if not summary and cve.get("descriptions"):
            summary = cve["descriptions"][0].get("value", "")

        cvss_score, cvss_version, severity = self._cvss(cve)
        products, versions = self._configurations(cve)
        return {
            "cve_id": cve_id,
            "source": "nvd",
            "summary": summary,
            "affected_products": products,
            "affected_versions": versions,
            "cvss_score": cvss_score,
            "cvss_version": cvss_version,
            "severity": severity,
            "published_at": cve.get("published", ""),
            "modified_at": cve.get("lastModified", ""),
            "source_url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
            "source_record_id": cve.get("sourceIdentifier", "") or cve_id,
        }

    def _cvss(self, cve: dict) -> Tuple[Optional[float], Optional[str], str]:
        metrics = cve.get("metrics", {})
        for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            for m in metrics.get(key, []):
                d = m.get("cvssData", {})
                score = d.get("baseScore")
                version = d.get("version", "")
                sev = (d.get("baseSeverity") or "").lower() or "info"
                return (score, version or None, sev)
        return (None, None, "info")

    def _configurations(self, cve: dict) -> Tuple[List[str], List[str]]:
        products: List[str] = []
        versions: List[str] = []
        for cfg in cve.get("configurations", []):
            for node in cfg.get("nodes", []):
                for cm in node.get("cpeMatch", []):
                    if cm.get("vulnerable") is False:
                        continue
                    product = self._cpe_product(cm.get("criteria", ""))
                    if product:
                        products.append(product)
                    versions.extend(self._cpe_ranges(cm))
        return list(dict.fromkeys(products)), list(dict.fromkeys(versions))

    @staticmethod
    def _cpe_product(criteria: str) -> Optional[str]:
        parts = criteria.split(":")
        if len(parts) < 6:
            return None
        product = parts[4].strip().lower()
        return product if product and product not in ("*", "-") else None

    @staticmethod
    def _cpe_ranges(cm: dict) -> List[str]:
        ranges: List[str] = []
        if cm.get("versionStartIncluding"):
            ranges.append(f">={cm['versionStartIncluding']}")
        elif cm.get("versionStartExcluding"):
            ranges.append(f">{cm['versionStartExcluding']}")
        if cm.get("versionEndIncluding"):
            ranges.append(f"<={cm['versionEndIncluding']}")
        elif cm.get("versionEndExcluding"):
            ranges.append(f"<{cm['versionEndExcluding']}")
        if not ranges:
            parts = cm.get("criteria", "").split(":")
            if len(parts) >= 6:
                ver = parts[5].strip().lower()
                if ver and ver not in ("*", "-"):
                    ranges.append(f"=={ver}")
        return ranges


class EpssSource:
    name = "epss"

    def __init__(
        self,
        base_url: str = "https://api.first.org/data/v1/epss",
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def fetch(
        self,
        client: Optional[httpx.AsyncClient] = None,
    ) -> Tuple[Dict[str, dict], dict]:
        own = client is None
        if own:
            client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=False)
        try:
            resp = await client.get(self.base_url)
            if resp.status_code == 429:
                raise SourceError("EPSS rate limited (HTTP 429)")
            if resp.status_code >= 500:
                raise SourceError(f"EPSS server error (HTTP {resp.status_code})")
            resp.raise_for_status()
            data = resp.json()
        finally:
            if own:
                await client.aclose()

        out: Dict[str, dict] = {}
        for entry in data.get("data", []):
            cve = entry.get("cve")
            if not validate_cve_id(cve):
                continue
            score = self._in_unit(entry.get("epss"))
            pct = self._in_unit(entry.get("percentile"))
            if score is None and pct is None:
                continue
            out[cve] = {
                "score": score,
                "percentile": pct,
                "date": entry.get("date", ""),
            }
        return out, {"status": "ok", "count": len(out)}

    @staticmethod
    def _in_unit(value) -> Optional[float]:
        try:
            f = float(value)
        except (TypeError, ValueError):
            return None
        return f if 0.0 <= f <= 1.0 else None


class KevSource:
    name = "cisa_kev"

    def __init__(
        self,
        base_url: str = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        timeout: float = 30.0,
    ):
        self.base_url = base_url
        self.timeout = timeout

    async def fetch(
        self,
        client: Optional[httpx.AsyncClient] = None,
    ) -> Tuple[Dict[str, dict], dict]:
        own = client is None
        if own:
            client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=False)
        try:
            resp = await client.get(self.base_url)
            if resp.status_code == 429:
                raise SourceError("KEV rate limited (HTTP 429)")
            if resp.status_code >= 500:
                raise SourceError(f"KEV server error (HTTP {resp.status_code})")
            resp.raise_for_status()
            data = resp.json()
        finally:
            if own:
                await client.aclose()

        out: Dict[str, dict] = {}
        for entry in data.get("vulnerabilities", []):
            cve = entry.get("cveID")
            if not validate_cve_id(cve):
                continue
            out[cve] = {
                "date_added": entry.get("dateAdded", ""),
                "name": entry.get("vulnerabilityName", ""),
                "due_date": entry.get("dueDate", ""),
            }
        return out, {"status": "ok", "count": len(out)}


__all__ = ["SourceError", "NvdSource", "EpssSource", "KevSource"]
