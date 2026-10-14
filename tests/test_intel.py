import asyncio

import core.intel as intel_mod
from core.advisories import Advisory, load_advisories, save_advisories


def _fake_source(fetch_result):
    class Fake:
        name = "fake"
        def __init__(self, *args, **kwargs):
            pass
        async def fetch(self, client=None):
            return fetch_result
    return Fake


def _fake_raising_source(exc):
    class Fake:
        name = "fake"
        def __init__(self, *args, **kwargs):
            pass
        async def fetch(self, client=None):
            raise exc
    return Fake


NVD_RECORDS = [{
    "cve_id": "CVE-2024-37032",
    "summary": "x",
    "affected_products": ["ollama"],
    "affected_versions": ["<0.1.34"],
    "cvss_score": 8.8,
    "cvss_version": "3.1",
    "severity": "high",
    "published_at": "",
    "modified_at": "",
    "source_url": "https://nvd.nist.gov/vuln/detail/CVE-2024-37032",
    "source_record_id": "cve@mitre.org",
}]


def _run(monkeypatch, tmp_path, nvd, epss, kev):
    monkeypatch.setattr(intel_mod, "NvdSource", nvd)
    monkeypatch.setattr(intel_mod, "EpssSource", epss)
    monkeypatch.setattr(intel_mod, "KevSource", kev)
    return asyncio.run(intel_mod.refresh_advisories(path=tmp_path / "cache.json"))


def test_merge_enriches_epss_and_kev(monkeypatch, tmp_path):
    res = _run(
        monkeypatch, tmp_path,
        _fake_source((NVD_RECORDS, {})),
        _fake_source(({"CVE-2024-37032": {"score": 0.5, "percentile": 0.9}}, {})),
        _fake_source(({"CVE-2024-37032": {"date_added": "d", "name": "n", "due_date": "x"}}, {})),
    )
    assert res["saved"] is True
    advs = load_advisories(tmp_path / "cache.json")
    assert advs[0].epss_score == 0.5
    assert advs[0].kev_listed is True


def test_kev_verified_absence_is_false(monkeypatch, tmp_path):
    _run(
        monkeypatch, tmp_path,
        _fake_source((NVD_RECORDS, {})),
        _fake_source(({}, {})),
        _fake_source(({}, {})),  # verified empty KEV snapshot
    )
    advs = load_advisories(tmp_path / "cache.json")
    assert advs[0].kev_listed is False


def test_kev_failure_is_unknown_not_false(monkeypatch, tmp_path):
    _run(
        monkeypatch, tmp_path,
        _fake_source((NVD_RECORDS, {})),
        _fake_source(({}, {})),
        _fake_raising_source(RuntimeError("kev down")),
    )
    advs = load_advisories(tmp_path / "cache.json")
    assert advs[0].kev_listed is None


def test_nvd_failure_preserves_existing_cache(monkeypatch, tmp_path):
    cache = tmp_path / "cache.json"
    save_advisories([Advisory(cve_id="CVE-2024-0001", source="nvd")], {"nvd": {"status": "ok"}}, cache)
    res = _run(
        monkeypatch, tmp_path,
        _fake_raising_source(RuntimeError("nvd down")),
        _fake_source(({}, {})),
        _fake_source(({}, {})),
    )
    assert res["saved"] is False
    advs = load_advisories(cache)
    assert [a.cve_id for a in advs] == ["CVE-2024-0001"]


def test_offline_first_run_reports_unavailable(monkeypatch, tmp_path):
    res = _run(
        monkeypatch, tmp_path,
        _fake_raising_source(RuntimeError("no net")),
        _fake_source(({}, {})),
        _fake_source(({}, {})),
    )
    assert res["saved"] is False
    assert res["sources"]["nvd"]["status"] == "failed"
