"""
Centralized, explainable risk grading.

This module keeps two orthogonal dimensions separate:

* **Risk grade** (``A``-``F``) is driven *only* by the worst confirmed
  finding severity. A single critical is always ``F``; a pile of lows can
  never dilute a critical back down to ``B``.
* **Coverage** (``full`` / ``partial`` / ``none``) describes how much was
  actually verified. ``unknown`` and ``error`` check results are *not* risk
  findings and do not change the letter grade; they reduce coverage. An
  ``A`` with ``partial`` coverage means "no confirmed findings, but not
  everything was verified" -- it is **not** a proof of safety.

The numeric ``risk_score`` is secondary to the letter grade and is capped to
the letter's band so the two never contradict each other.
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

_BAND_MAX = {"A": 9, "B": 24, "C": 39, "D": 59, "F": 100}


def _severity(item: dict) -> str:
    sev = str(item.get("severity", "info") or "info").lower()
    return sev if sev in SEVERITY_ORDER else "info"


def compute_grade(
    findings: Iterable[dict],
    check_results: Optional[Dict[str, str]] = None,
) -> Tuple[str, int, List[str], Dict]:
    """Return ``(grade, risk_score, reasons, coverage_info)``.

    ``coverage_info`` is::

        {
          "coverage": {"total", "pass", "fail", "warn", "error", "unknown"},
          "coverage_status": "full" | "partial" | "none",
        }
    """
    findings = list(findings)
    reasons: List[str] = []
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    worst = "none" if not findings else "info"
    for f in findings:
        sev = _severity(f)
        counts[sev] = counts.get(sev, 0) + 1
        if SEVERITY_ORDER[sev] > SEVERITY_ORDER.get(worst, 0):
            worst = sev

    grade = _GRADE_BY_SEVERITY[worst]
    reasons.append(f"worst finding severity: {worst}")

    total = sum(counts.values())
    score = _BASE_SCORE.get(worst, 0) + min(total * 2, 20)
    score = min(_BAND_MAX.get(grade, 100), score)

    for sev in ("critical", "high", "medium", "low", "info"):
        if counts[sev]:
            reasons.append(f"{sev}: {counts[sev]}")

    coverage = {"total": 0, "pass": 0, "fail": 0, "warn": 0, "error": 0, "unknown": 0}
    if check_results:
        for status in check_results.values():
            s = str(status).lower()
            if s in coverage:
                coverage[s] += 1
                coverage["total"] += 1

    if coverage["total"] == 0:
        coverage_status = "none"
    elif coverage["error"] or coverage["unknown"]:
        coverage_status = "partial"
    else:
        coverage_status = "full"

    if coverage["error"]:
        reasons.append(
            f"coverage: {coverage['error']} check(s) errored and were not assessed"
        )
    if coverage["unknown"]:
        reasons.append(
            f"coverage: {coverage['unknown']} check(s) could not be verified"
        )

    return grade, score, reasons, {
        "coverage": coverage,
        "coverage_status": coverage_status,
    }


def _threshold_rank(threshold: str) -> int:
    rank = SEVERITY_ORDER.get(str(threshold).lower())
    if rank is None:
        raise ValueError(f"invalid fail-on threshold: {threshold}")
    return rank


def fail_gate_triggered(findings, threshold: str) -> bool:
    """True when a ``confirmed`` finding reaches the threshold severity.

    ``unknown``/``error``/coverage and non-confirmed findings never trigger
    the gate, and never silently become a clean pass.
    """
    rank = _threshold_rank(threshold)
    for f in findings:
        if str(f.get("confidence", "")).lower() != "confirmed":
            continue
        sev = str(f.get("severity", "info")).lower()
        if SEVERITY_ORDER.get(sev, 0) >= rank:
            return True
    return False


def confirmed_findings_above(findings, threshold: str) -> list:
    rank = _threshold_rank(threshold)
    out = []
    for f in findings:
        if str(f.get("confidence", "")).lower() != "confirmed":
            continue
        sev = str(f.get("severity", "info")).lower()
        if SEVERITY_ORDER.get(sev, 0) >= rank:
            out.append(f)
    return out


__all__ = [
    "compute_grade",
    "SEVERITY_ORDER",
    "fail_gate_triggered",
    "confirmed_findings_above",
]
