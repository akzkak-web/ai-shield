from core.rating import compute_grade


def _grade(findings, check_results=None):
    grade, score, reasons, cov = compute_grade(findings, check_results)
    return grade, score, reasons, cov


def test_single_critical():
    grade, score, _, _ = _grade([{"severity": "critical"}], {})
    assert grade == "F"
    assert score >= 60


def test_single_high():
    grade, _, _, _ = _grade([{"severity": "high"}], {})
    assert grade == "D"


def test_multiple_low():
    grade, _, _, _ = _grade([{"severity": "low"}] * 5, {})
    assert grade == "B"


def test_critical_not_diluted_by_lows():
    findings = [{"severity": "critical"}] + [{"severity": "low"}] * 20
    grade, _, _, _ = _grade(findings, {})
    assert grade == "F"


def test_all_pass_full_coverage():
    grade, score, _, cov = _grade([], {"auth_missing": "pass", "cve_check": "pass"})
    assert grade == "A"
    assert score == 0
    assert cov["coverage_status"] == "full"


def test_error_not_treated_as_vulnerability():
    grade, _, reasons, cov = _grade([], {"auth_missing": "pass", "cve_check": "error"})
    assert grade == "A"
    assert cov["coverage_status"] == "partial"
    assert any("errored" in r for r in reasons)


def test_unknown_not_treated_as_pass():
    grade, _, reasons, cov = _grade([], {"cve_check": "unknown"})
    assert grade == "A"
    assert cov["coverage_status"] == "partial"
    assert any("could not be verified" in r for r in reasons)


def test_no_check_results_none_coverage():
    _, _, _, cov = _grade([])
    assert cov["coverage_status"] == "none"


def test_high_not_affected_by_error():
    grade, _, _, cov = _grade([{"severity": "high"}], {"cve_check": "error"})
    assert grade == "D"
    assert cov["coverage_status"] == "partial"
