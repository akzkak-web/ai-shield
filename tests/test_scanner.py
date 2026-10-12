import asyncio

import pytest

import core.scanner as scanner_mod
from checks import CheckResult, CheckStatus, Finding
from core.scanner import ScanResult, Scanner


def _finding(severity="critical"):
    return Finding(
        check_id="T-001",
        check_name="test",
        severity=severity,
        title_zh="x",
        title_en="x",
        description_zh="x",
        description_en="x",
    )


def test_expand_target_cidr():
    ips = Scanner.expand_target("10.0.0.0/30")
    assert ips == ["10.0.0.1", "10.0.0.2"]


def test_scan_result_grade_with_check_results():
    r = ScanResult("127.0.0.1")
    r.findings.append(_finding("critical"))
    r.check_results = {"auth_missing": "fail", "cve_check": "error"}
    r.calculate_grade()
    assert r.grade == "F"
    assert "grade_reasons" in r.to_dict()


def test_run_scan_rejects_public_target():
    with pytest.raises(ValueError):
        asyncio.run(Scanner().run_scan("8.8.8.8"))


def test_run_scan_records_check_error(monkeypatch, tmp_path):
    async def fake_scan_ports(host, ports, timeout=2.0):
        return {
            "host": host,
            "total_scanned": len(ports),
            "open_ports": [11434],
            "services": [
                {"port": 11434, "service": "Ollama", "version": "0.1.33", "detected": True}
            ],
        }

    async def ok_check(host, port, service, version=None, client=None):
        return CheckResult("ok_check", CheckStatus.FAIL, [_finding("critical")])

    async def boom_check(host, port, service, version=None, client=None):
        raise RuntimeError("boom")

    monkeypatch.setattr(scanner_mod, "scan_ports", fake_scan_ports)
    monkeypatch.setattr(scanner_mod, "ALL_CHECKS", {"ok_check": ok_check, "boom_check": boom_check})

    sc = Scanner()
    sc.history_file = tmp_path / "history.json"
    result = asyncio.run(sc.run_scan("127.0.0.1", [11434], ["ok_check", "boom_check"]))

    assert result["check_results"]["boom_check"] == "error"
    assert result["check_results"]["ok_check"] == "fail"
    assert len(result["findings"]) == 1
    assert result["grade"] == "F"
