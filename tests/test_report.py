import shutil
import subprocess

import pytest

import core.report as report_mod
from core.report import generate_pdf_report
from core.scanner import ScanResult


def test_json_report_structure():
    r = ScanResult("127.0.0.1")
    r.check_results = {"auth_missing": "unknown", "cve_check": "pass"}
    r.calculate_grade()
    d = r.to_dict()
    for key in ("id", "target", "grade", "risk_score", "grade_reasons",
                "coverage", "coverage_status", "notes",
                "findings", "check_results", "summary", "port_data"):
        assert key in d


def test_pdf_report_generation(tmp_path):
    r = ScanResult("127.0.0.1")
    r.check_results = {"auth_missing": "pass"}
    r.calculate_grade()
    out = tmp_path / "report.pdf"
    path = generate_pdf_report(r.to_dict(), str(out))
    assert path == str(out)
    assert out.exists() and out.stat().st_size > 0


def test_pdf_report_unicode_em_dash(tmp_path):
    if report_mod._find_font(report_mod._LATIN_FONT_CANDIDATES) is None:
        pytest.skip("no Latin Unicode font available")
    r = ScanResult("127.0.0.1")
    r.check_results = {"auth_missing": "pass"}
    r.calculate_grade()
    r.grade_reasons = ["no AI services identified — nothing to scan"]
    out = tmp_path / "report.pdf"
    generate_pdf_report(r.to_dict(), str(out))
    assert out.exists() and out.stat().st_size > 0


def test_pdf_report_chinese_and_dynamic_fields(tmp_path):
    if report_mod._find_font(report_mod._CJK_FONT_CANDIDATES) is None:
        pytest.skip("no CJK font available")
    r = ScanResult("127.0.0.1")
    r.check_results = {"auth_missing": "unknown"}
    r.calculate_grade()
    r.grade_reasons = ["未发现 AI 服务", "服务未认证"]
    out = tmp_path / "report.pdf"
    generate_pdf_report(r.to_dict(), str(out))
    assert out.exists() and out.stat().st_size > 0


def test_pdf_report_ascii_works_without_unicode_font(monkeypatch, tmp_path):
    monkeypatch.setattr(report_mod, "_find_font", lambda candidates: None)
    r = ScanResult("127.0.0.1")
    r.grade_reasons = ["no findings"]
    r.check_results = {"auth_missing": "pass"}
    r.calculate_grade()
    out = tmp_path / "report.pdf"
    generate_pdf_report(r.to_dict(), str(out))
    assert out.exists() and out.stat().st_size > 0


def test_selected_fonts_cover_required_characters():
    pytest.importorskip("fontTools.ttLib")
    from fontTools.ttLib import TTFont

    latin = report_mod._find_font(report_mod._LATIN_FONT_CANDIDATES)
    cjk = report_mod._find_font(report_mod._CJK_FONT_CANDIDATES)
    if latin is None or cjk is None:
        pytest.skip("required Unicode fonts are not installed")

    latin_cmap = TTFont(latin).getBestCmap()
    cjk_cmap = TTFont(cjk).getBestCmap()

    for ch in "Local AI Service0123—":
        assert ord(ch) in latin_cmap, f"Latin font missing {ch!r}"
    for ch in "安全扫描报告服务未认证":
        assert ord(ch) in cjk_cmap, f"CJK font missing {ch!r}"


def test_pdf_mixed_unicode_text_layer(tmp_path):
    if shutil.which("mutool") is None:
        pytest.skip("mutool not available for PDF text extraction")
    if report_mod._find_font(report_mod._LATIN_FONT_CANDIDATES) is None:
        pytest.skip("no Latin Unicode font available")
    if report_mod._find_font(report_mod._CJK_FONT_CANDIDATES) is None:
        pytest.skip("no CJK font available")

    r = ScanResult("127.0.0.1")
    r.check_results = {"auth_missing": "unknown"}
    r.calculate_grade()
    r.grade_reasons = ["安全扫描报告 — Local AI Service 123", "服务未认证"]
    out = tmp_path / "report.pdf"
    generate_pdf_report(r.to_dict(), str(out))

    text = subprocess.run(
        ["mutool", "draw", "-F", "txt", str(out)],
        capture_output=True,
        text=True,
    ).stdout

    assert "安全扫描报告" in text
    assert "Local AI Service" in text
    assert "服务未认证" in text
    assert "—" in text
