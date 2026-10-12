from core.rating import compute_grade


def test_single_critical():
    grade, score, _ = compute_grade([{"severity": "critical"}], {})
    assert grade == "F"
    assert score >= 60


def test_single_high():
    grade, _, _ = compute_grade([{"severity": "high"}], {})
    assert grade == "D"


def test_multiple_low():
    grade, _, _ = compute_grade([{"severity": "low"}] * 5, {})
    assert grade == "B"


def test_critical_not_diluted_by_lows():
    findings = [{"severity": "critical"}] + [{"severity": "low"}] * 20
    grade, _, _ = compute_grade(findings, {})
    assert grade == "F"


def test_all_pass():
    grade, score, _ = compute_grade([], {"auth_missing": "pass", "cve_check": "pass"})
    assert grade == "A"
    assert score == 0


def test_partial_check_failure_caps_grade():
    grade, _, _ = compute_grade([], {"auth_missing": "pass", "cve_check": "error"})
    assert grade == "C"


def test_unknown_version_not_secure():
    grade, _, _ = compute_grade([], {"cve_check": "unknown"})
    assert grade != "A"


def test_high_not_downgraded_by_error():
    # A high finding is already worse than the "C" error cap.
    grade, _, _ = compute_grade([{"severity": "high"}], {"cve_check": "error"})
    assert grade == "D"
