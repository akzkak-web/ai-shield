import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from core.rating import confirmed_findings_above, fail_gate_triggered


ROOT = Path(__file__).resolve().parent.parent


def _finding(severity, confidence="confirmed"):
    return {"severity": severity, "confidence": confidence}


def test_fail_gate_critical_threshold():
    assert fail_gate_triggered([_finding("critical")], "critical") is True
    assert fail_gate_triggered([_finding("high")], "critical") is False
    assert fail_gate_triggered([_finding("medium")], "critical") is False
    assert fail_gate_triggered([_finding("low")], "critical") is False


def test_fail_gate_high_threshold_includes_critical():
    assert fail_gate_triggered([_finding("high")], "high") is True
    assert fail_gate_triggered([_finding("critical")], "high") is True
    assert fail_gate_triggered([_finding("medium")], "high") is False


def test_fail_gate_medium_and_low():
    assert fail_gate_triggered([_finding("medium")], "medium") is True
    assert fail_gate_triggered([_finding("low")], "medium") is False
    assert fail_gate_triggered([_finding("low")], "low") is True


def test_non_confirmed_never_triggers():
    assert fail_gate_triggered([_finding("critical", "likely")], "critical") is False
    assert fail_gate_triggered([_finding("critical", "possible")], "critical") is False


def test_info_never_triggers():
    assert fail_gate_triggered([_finding("info")], "low") is False


def test_no_findings_or_unknown():
    assert fail_gate_triggered([], "high") is False
    # unknown/error are not findings at all.
    assert fail_gate_triggered([{"severity": "info", "confidence": ""}], "high") is False


def test_invalid_threshold_raises():
    with pytest.raises(ValueError):
        fail_gate_triggered([_finding("critical")], "bogus")


def test_confirmed_findings_above():
    fs = [_finding("critical"), _finding("high"), _finding("medium", "likely"), _finding("low")]
    above = confirmed_findings_above(fs, "high")
    assert [f["severity"] for f in above] == ["critical", "high"]


def _load_cli():
    spec = importlib.util.spec_from_file_location("ai_shield_cli", str(ROOT / "ai-shield.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gate_helper_exit_codes():
    cli = _load_cli()
    code, msg = cli._gate([_finding("critical")], "high")
    assert code == 1
    assert "FAILED" in msg
    code, msg = cli._gate([_finding("low")], "high")
    assert code == 0
    assert "PASS" in msg
    # partial coverage is qualified, not silently a clean pass
    code, msg = cli._gate([], "high", coverage_status="partial")
    assert code == 0
    assert "NOT a security guarantee" in msg


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "ai-shield.py", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_cli_version_outputs_project_version():
    proc = _run_cli("--version")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "0.1.0-rc.1"


def test_cli_target_rejected_exit_2():
    proc = _run_cli("scan", "8.8.8.8")
    assert proc.returncode == 2


def test_cli_invalid_fail_on_exit_2():
    proc = _run_cli("scan", "--fail-on", "bogus", "127.0.0.1")
    assert proc.returncode == 2


def test_cli_no_services_exit_0():
    proc = _run_cli("scan", "127.0.0.1", "--ports", "1")
    assert proc.returncode == 0
    assert "Fail gate" in proc.stdout
