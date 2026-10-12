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
