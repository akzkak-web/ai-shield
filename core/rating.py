"""
Centralized, explainable risk grading.

Every consumer (CLI, web UI, JSON report, PDF report) must call this single
function so that a finding always maps to the same grade. The rules are
intentionally simple and monotonic:

1. The letter grade is a hard *ceiling* set by the worst finding severity:
   critical -> F, high -> D, medium -> C, low -> B, info/none -> A.
2. A single critical therefore can never be diluted back to B by a large
   number of low findings.
3. ``error`` check results cap the grade at C (we cannot claim a target is
   safe when a check failed).
4. ``unknown`` check results prevent a clean ``A`` when there are no
   findings (unverified is not "secure").
5. The numeric risk score is base(worst severity) + a small count factor,
   capped at 100. It is monotonic but secondary to the letter grade.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple


SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

_BASE_SCORE = {"none": 0, "info": 5, "low": 18, "medium": 32, "high": 50, "critical": 75}

_GRADE_BY_SEVERITY = {
    "none": "A",
    "critical": "F",
    "high": "D",
    "medium": "C",
    "low": "B",
    "info": "A",
}

_GRADE_RANK = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}
_BAND_MAX = {"A": 9, "B": 24, "C": 39, "D": 59, "F": 100}


def _severity(item: dict) -> str:
    sev = str(item.get("severity", "info") or "info").lower()
    return sev if sev in SEVERITY_ORDER else "info"


def _worse_grade(a: str, b: str) -> str:
    """Return the worse (higher-risk) of two grades."""
    return a if _GRADE_RANK.get(a, 0) >= _GRADE_RANK.get(b, 0) else b


def compute_grade(
    findings: Iterable[dict],
    check_results: Optional[Dict[str, str]] = None,
) -> Tuple[str, int, List[str]]:
    """Return ``(grade, risk_score, reasons)``.

    ``findings`` is an iterable of finding dicts (each with at least a
    ``severity`` key). ``check_results`` is an optional mapping of
    check-name -> status (``pass``/``fail``/``warn``/``error``/``unknown``).
    """
    findings = list(findings)
    reasons: List[str] = []
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    worst = "none" if not findings else "info"
    for f in findings:
        sev = _severity(f)
        counts[sev] = counts.get(sev, 0) + 1
        if SEVERITY_ORDER[sev] > SEVERITY_ORDER[worst]:
            worst = sev

    grade = _GRADE_BY_SEVERITY[worst]
    reasons.append(f"worst finding severity: {worst}")

    statuses: Dict[str, int] = {"pass": 0, "fail": 0, "warn": 0, "error": 0, "unknown": 0}
    if check_results:
        for status in check_results.values():
            s = str(status).lower()
            if s in statuses:
                statuses[s] += 1

    # Coverage adjustments.
    if statuses["error"]:
        capped = _worse_grade(grade, "C")
        if capped != grade:
            reasons.append(
                f"{statuses['error']} check(s) failed to run; grade capped at C"
            )
        grade = capped
    if statuses["unknown"] and worst in ("info", "none"):
        capped = _worse_grade(grade, "B")
        if capped != grade:
            reasons.append(
                f"{statuses['unknown']} check(s) could not be verified; cannot report 'A'"
            )
        grade = capped

    total = sum(counts.values())
    score = _BASE_SCORE.get(worst, 0) + min(total * 2, 20)
    score = min(_BAND_MAX.get(grade, 100), score)

    for sev in ("critical", "high", "medium", "low", "info"):
        if counts[sev]:
            reasons.append(f"{sev}: {counts[sev]}")

    return grade, score, reasons


__all__ = ["compute_grade", "SEVERITY_ORDER"]
