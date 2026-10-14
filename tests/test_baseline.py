import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.baseline import (
    BaselineError,
    build_baseline,
    compare_baseline,
    fingerprint,
    load_baseline,
    new_confirmed_above,
    sanitize_evidence,
    save_baseline,
)


ROOT = Path(__file__).resolve().parent.parent


def _f(check_id="AUTH-001", check_name="auth_missing", severity="critical",
       confidence="confirmed", service="Ollama", port=11434, evidence="no auth"):
    return {
        "check_id": check_id,
        "check_name": check_name,
        "severity": severity,
        "confidence": confidence,
        "service": service,
        "port": port,
        "evidence": evidence,
    }


def _result(findings, check_results, target="127.0.0.1", coverage="full", grade="F"):
    return {
        "target": target,
        "coverage_status": coverage,
        "grade": grade,
        "findings": findings,
        "check_results": check_results,
    }


def test_fingerprint_stable_and_distinct():
    a = _f(evidence="different evidence text")
    b = _f(evidence="completely different")
    assert fingerprint(a) == fingerprint(b)
    assert fingerprint(_f(service="vLLM", port=8000)) != fingerprint(a)
    assert fingerprint(_f(port=1234)) != fingerprint(a)


def test_sanitize_evidence_masks_secrets():
    out = sanitize_evidence("token=abc123 email=user@example.com Authorization: Bearer xyz github_pat_ABC")
    assert "abc123" not in out
    assert "user@example.com" not in out
    assert "github_pat_" not in out


def test_build_baseline_shape_and_no_raw_secret(tmp_path):
    f = _f(evidence="Authorization: Bearer SECRET-TOKEN user@example.com")
    baseline = build_baseline(_result([f], {"auth_missing": "fail"}))
    assert baseline["schema_version"] == 2
    assert baseline["target"] == "127.0.0.1"
    assert baseline["findings"][0]["fingerprint"] == fingerprint(f)
    assert "SECRET-TOKEN" not in json.dumps(baseline)
    assert "user@example.com" not in json.dumps(baseline)


def test_save_load_roundtrip(tmp_path):
    p = tmp_path / "baseline.json"
    baseline = build_baseline(_result([_f()], {"auth_missing": "fail"}))
    save_baseline(baseline, p)
    assert load_baseline(p)["findings"][0]["check_id"] == "AUTH-001"
    # no temp files left behind
    assert [x.name for x in tmp_path.iterdir() if x.name.startswith(".baseline-")] == []


def test_load_corrupt_and_unknown_schema(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(BaselineError):
        load_baseline(p)
    p.write_text(json.dumps({"schema_version": 999, "target": "x", "findings": []}))
    with pytest.raises(BaselineError):
        load_baseline(p)


def test_compare_new_fixed_persistent():
    base = build_baseline(_result([_f()], {"auth_missing": "fail"}))
    # current: nothing -> the check passed -> fixed
    current = _result([], {"auth_missing": "pass"}, grade="A")
    diff = compare_baseline(base, current)
    assert diff["summary"] == {"fixed": 1}


def test_compare_persistent_and_changed():
    base = build_baseline(_result([_f(severity="high")], {"auth_missing": "fail"}))
    # severity changed high -> critical
    current = _result([_f(severity="critical")], {"auth_missing": "fail"})
    diff = compare_baseline(base, current)
    assert diff["summary"] == {"changed": 1}
    assert diff["entries"][0]["previous_severity"] == "high"

    # unchanged -> persistent
    current2 = _result([_f(severity="high")], {"auth_missing": "fail"})
    diff2 = compare_baseline(base, current2)
    assert diff2["summary"] == {"persistent": 1}


def test_compare_new_when_baseline_empty():
    base = build_baseline(_result([], {}))
    current = _result([_f()], {"auth_missing": "fail"})
    diff = compare_baseline(base, current)
    assert diff["summary"] == {"new": 1}


def test_target_mismatch_raises():
    base = build_baseline(_result([], {}, target="127.0.0.1"))
    current = _result([], {}, target="192.168.1.10")
    with pytest.raises(BaselineError):
        compare_baseline(base, current)


def test_not_scanned_cannot_be_fixed():
    base = build_baseline(_result([_f()], {"auth_missing": "fail"}))
    # check not run at all -> unknown, not fixed
    current = _result([], {}, coverage="none", grade="N/A")
    diff = compare_baseline(base, current)
    assert diff["summary"] == {"unknown": 1}
    assert diff["entries"][0]["reason"].startswith("not fixed")


def test_unknown_or_error_cannot_be_fixed():
    base = build_baseline(_result([_f()], {"auth_missing": "fail"}))
    for status in ("unknown", "error"):
        current = _result([], {"auth_missing": status}, coverage="partial", grade="B")
        diff = compare_baseline(base, current)
        assert diff["summary"] == {"unknown": 1}


def test_intel_unavailable_does_not_erase_history():
    cve = _f(check_id="CVE-CVE-2024-37032", check_name="cve_check", severity="high", service="Ollama", port=11434)
    base = build_baseline(_result([cve], {"cve_check": "fail"}))
    # intel unavailable -> cve_check unknown, no finding -> NOT fixed
    current = _result([], {"cve_check": "unknown"}, coverage="partial", grade="B")
    diff = compare_baseline(base, current)
    assert diff["summary"] == {"unknown": 1}


def test_new_confirmed_above_threshold():
    entries = [
        {"status": "new", "severity": "critical", "confidence": "confirmed"},
        {"status": "new", "severity": "low", "confidence": "confirmed"},
        {"status": "new", "severity": "high", "confidence": "likely"},
        {"status": "persistent", "severity": "high", "confidence": "confirmed"},
    ]
    above = new_confirmed_above(entries, "high")
    assert [e["severity"] for e in above] == ["critical"]


def test_persistent_high_does_not_trigger_new_gate():
    entries = [{"status": "persistent", "severity": "critical", "confidence": "confirmed"}]
    assert new_confirmed_above(entries, "high") == []


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "ai-shield.py", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_cli_baseline_out_and_compare(tmp_path):
    bl = tmp_path / "baseline.json"
    proc = _run_cli("scan", "127.0.0.1", "--ports", "1", "--baseline-out", str(bl))
    assert proc.returncode == 0
    assert bl.exists()
    diff = tmp_path / "diff.json"
    proc2 = _run_cli("scan", "127.0.0.1", "--ports", "1", "--baseline", str(bl), "--diff-json", str(diff))
    assert proc2.returncode == 0
    assert diff.exists()
    data = json.loads(diff.read_text())
    assert "summary" in data


def test_cli_missing_baseline_exit_2():
    proc = _run_cli("scan", "127.0.0.1", "--ports", "1", "--baseline", "/nonexistent-baseline.json")
    assert proc.returncode == 2
