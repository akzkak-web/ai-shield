import json

from core.advisories import (
    Advisory,
    cache_status,
    cvss_to_severity,
    load_advisories,
    match_advisories,
    save_advisories,
    validate_cve_id,
)


def _write(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_validate_cve_id():
    assert validate_cve_id("CVE-2024-37032")
    assert validate_cve_id("CVE-1999-0001")
    assert not validate_cve_id("CVE-2024-37")
    assert not validate_cve_id("bad")
    assert not validate_cve_id("")


def test_cvss_to_severity():
    assert cvss_to_severity(None) == "info"
    assert cvss_to_severity(9.8) == "critical"
    assert cvss_to_severity(8.8) == "high"
    assert cvss_to_severity(5.5) == "medium"
    assert cvss_to_severity(3.1) == "low"
    assert cvss_to_severity(0.0) == "info"


def test_load_advisories_valid_and_invalid(tmp_path):
    p = _write(tmp_path / "a.json", {
        "advisories": [
            {
                "cve_id": "CVE-2024-37032",
                "source": "nvd",
                "affected_products": ["ollama"],
                "affected_versions": ["<0.1.34"],
                "cvss_score": 8.8,
                "cvss_version": "3.1",
                "kev_listed": True,
            },
            {"cve_id": "not-a-cve", "source": "nvd"},  # invalid cve id -> skipped
            {"source": "nvd"},  # missing cve id -> skipped
            {"cve_id": "CVE-2024-0001", "source": "nvd", "cvss_score": 99.9},  # out-of-range cvss
        ]
    })
    advs = load_advisories(p)
    assert [a.cve_id for a in advs] == ["CVE-2024-37032", "CVE-2024-0001"]
    assert advs[0].cvss_score == 8.8
    assert advs[0].kev_listed is True
    assert advs[1].cvss_score is None


def test_kev_listed_tri_state(tmp_path):
    # "false" as a string is NOT a boolean -> unknown (None), never fabricated False.
    p = _write(tmp_path / "a.json", {
        "advisories": [
            {"cve_id": "CVE-2024-0001", "source": "nvd", "kev_listed": "false"},
            {"cve_id": "CVE-2024-0002", "source": "nvd", "kev_listed": False},
        ]
    })
    advs = load_advisories(p)
    assert advs[0].kev_listed is None
    assert advs[1].kev_listed is False


def test_epss_out_of_range_unknown(tmp_path):
    p = _write(tmp_path / "a.json", {
        "advisories": [
            {"cve_id": "CVE-2024-0001", "source": "nvd", "epss_score": 1.5, "epss_percentile": 0.8},
        ]
    })
    advs = load_advisories(p)
    assert advs[0].epss_score is None
    assert advs[0].epss_percentile == 0.8


def test_match_affected_not_affected_unknown(tmp_path):
    p = _write(tmp_path / "a.json", {
        "advisories": [
            {"cve_id": "CVE-2024-37032", "source": "nvd",
             "affected_products": ["ollama"], "affected_versions": ["<0.1.34"]},
        ]
    })
    assert [(a.cve_id, s) for a, s in match_advisories("Ollama", "0.1.33", p)] == [("CVE-2024-37032", "affected")]
    assert [(a.cve_id, s) for a, s in match_advisories("Ollama", "0.1.34", p)] == [("CVE-2024-37032", "not_affected")]
    assert [(a.cve_id, s) for a, s in match_advisories("Ollama", None, p)] == [("CVE-2024-37032", "unknown")]


def test_match_similar_name_not_confused(tmp_path):
    p = _write(tmp_path / "a.json", {
        "advisories": [
            {"cve_id": "CVE-2024-37032", "source": "nvd",
             "affected_products": ["ollama"], "affected_versions": ["<0.1.34"]},
        ]
    })
    # "llama.cpp / LocalAI" should NOT match product "ollama".
    assert match_advisories("llama.cpp / LocalAI", "1.0", p) == []


def test_cache_status(tmp_path):
    p = tmp_path / "cache.json"
    assert cache_status(100, p) == "unavailable"
    save_advisories([], {}, p)  # retrieved_at = now -> fresh
    assert cache_status(100000, p) == "fresh"
    _write(p, {"retrieved_at": "2000-01-01T00:00:00Z", "advisories": []})
    assert cache_status(100000, p) == "stale"


def test_corrupt_cache_returns_unavailable(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    assert load_advisories(p) == []
    assert cache_status(100, p) == "unavailable"


def test_save_is_atomic_and_does_not_leave_temp_files(tmp_path):
    p = tmp_path / "cache.json"
    adv = Advisory(cve_id="CVE-2024-0001", source="nvd")
    save_advisories([adv], {"nvd": {"status": "ok"}}, p)
    assert p.exists()
    assert load_advisories(p)[0].cve_id == "CVE-2024-0001"
    temps = [f.name for f in tmp_path.iterdir() if f.name.startswith(".advisories-")]
    assert temps == []
