import asyncio

import httpx
import pytest

from core.sources import EpssSource, KevSource, NvdSource, SourceError


def make_client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def run(coro):
    return asyncio.run(coro)


NVD_OK = {
    "resultsPerPage": 10,
    "startIndex": 0,
    "totalResults": 1,
    "vulnerabilities": [{"cve": {
        "id": "CVE-2024-37032",
        "sourceIdentifier": "cve@mitre.org",
        "published": "2024-05-31T04:15:09.617",
        "lastModified": "2026-06-17T07:37:38.427",
        "descriptions": [{"lang": "en", "value": "Ollama path traversal"}],
        "metrics": {"cvssMetricV31": [{"cvssData": {"version": "3.1", "baseScore": 8.8, "baseSeverity": "HIGH"}}]},
        "configurations": [{"nodes": [{"cpeMatch": [{
            "vulnerable": True,
            "criteria": "cpe:2.3:a:ollama:ollama:*:*:*:*:*:*:*:*",
            "versionEndExcluding": "0.1.34",
        }]}]}],
    }}],
}


def test_nvd_parse_valid():
    async def main():
        client = make_client(lambda req: httpx.Response(200, json=NVD_OK))
        try:
            records, meta = await NvdSource().fetch(client=client)
            return records, meta
        finally:
            await client.aclose()

    records, meta = run(main())
    assert len(records) == 1
    r = records[0]
    assert r["cve_id"] == "CVE-2024-37032"
    assert r["cvss_score"] == 8.8
    assert r["cvss_version"] == "3.1"
    assert r["affected_products"] == ["ollama"]
    assert r["affected_versions"] == ["<0.1.34"]


def test_nvd_429():
    async def main():
        client = make_client(lambda req: httpx.Response(429))
        try:
            with pytest.raises(SourceError):
                await NvdSource().fetch(client=client)
        finally:
            await client.aclose()

    run(main())


def test_nvd_500():
    async def main():
        client = make_client(lambda req: httpx.Response(500))
        try:
            with pytest.raises(SourceError):
                await NvdSource().fetch(client=client)
        finally:
            await client.aclose()

    run(main())


def test_nvd_timeout():
    async def main():
        def handler(req):
            raise httpx.TimeoutException("timeout")
        client = make_client(handler)
        try:
            with pytest.raises(httpx.TimeoutException):
                await NvdSource().fetch(client=client)
        finally:
            await client.aclose()

    run(main())


def test_nvd_missing_cvss():
    body = {"totalResults": 1, "resultsPerPage": 10, "startIndex": 0,
            "vulnerabilities": [{"cve": {"id": "CVE-2024-0001", "descriptions": [],
                                          "configurations": []}}]}
    async def main():
        client = make_client(lambda req: httpx.Response(200, json=body))
        try:
            records, _ = await NvdSource().fetch(client=client)
            return records
        finally:
            await client.aclose()
    records = run(main())
    assert records[0]["cvss_score"] is None


def test_nvd_api_key_not_in_output_and_in_header():
    captured = {}
    async def main():
        def handler(req):
            captured["apiKey"] = req.headers.get("apiKey")
            return httpx.Response(200, json=NVD_OK)
        client = make_client(handler)
        try:
            records, _ = await NvdSource(api_key="SECRET-KEY").fetch(client=client)
            return records
        finally:
            await client.aclose()
    records = run(main())
    assert captured["apiKey"] == "SECRET-KEY"
    assert "SECRET-KEY" not in str(records)


def test_epss_parse_and_invalid():
    body = {"status": "OK", "data": [
        {"cve": "CVE-2024-37032", "epss": "0.5", "percentile": "0.9", "date": "2024-01-01"},
        {"cve": "CVE-2024-0002", "epss": "2.0", "percentile": "0.5", "date": "2024-01-01"},  # out of range
        {"cve": "CVE-2024-0003", "epss": "0.1", "percentile": "bad", "date": "2024-01-01"},  # bad percentile
    ]}
    async def main():
        client = make_client(lambda req: httpx.Response(200, json=body))
        try:
            data, _ = await EpssSource().fetch(client=client)
            return data
        finally:
            await client.aclose()
    data = run(main())
    assert data["CVE-2024-37032"]["score"] == 0.5
    assert data["CVE-2024-37032"]["percentile"] == 0.9
    # out-of-range epss -> score None; percentile present -> still included
    assert data["CVE-2024-0002"]["score"] is None
    assert data["CVE-2024-0003"]["percentile"] is None


def test_kev_parse():
    body = {"vulnerabilities": [{
        "cveID": "CVE-2024-37032",
        "dateAdded": "2024-06-01",
        "vulnerabilityName": "Ollama Path Traversal",
        "dueDate": "2024-06-22",
    }]}
    async def main():
        client = make_client(lambda req: httpx.Response(200, json=body))
        try:
            data, _ = await KevSource().fetch(client=client)
            return data
        finally:
            await client.aclose()
    data = run(main())
    assert data["CVE-2024-37032"]["date_added"] == "2024-06-01"
