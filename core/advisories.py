"""
Verified security advisories.

This module loads a small, human-reviewed advisory database from
``data/advisories.json``. Every entry must trace back to an authoritative
source (NVD, OSV, GHSA, or an upstream security advisory) and carry a
``retrieved_at`` timestamp and a source URL.

The previous ``CVE_DB`` contained fabricated identifiers and wrong
affected-version ranges. Nothing here is synthesized: if we cannot verify
an advisory, we do not ship it, and the CVE check reports "unknown" instead
of inventing a conclusion.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from core.versioning import parse_version, version_in_ranges, Version


_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "advisories.json"


@dataclass(frozen=True)
class Advisory:
    id: str
    source: str
    product: str
    affected: tuple
    fixed: Optional[str]
    severity: str
    summary_en: str
    summary_zh: str
    url: str
    retrieved_at: str


def load_advisories(path: Optional[Path] = None) -> List[Advisory]:
    p = path or _DATA_FILE
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out: List[Advisory] = []
    for item in raw.get("advisories", []):
        try:
            out.append(
                Advisory(
                    id=item["id"],
                    source=item.get("source", ""),
                    product=item.get("product", ""),
                    affected=tuple(item.get("affected", [])),
                    fixed=item.get("fixed"),
                    severity=item.get("severity", "high"),
                    summary_en=item.get("summary_en", ""),
                    summary_zh=item.get("summary_zh", ""),
                    url=item.get("url", ""),
                    retrieved_at=item.get("retrieved_at", ""),
                )
            )
        except KeyError:
            continue
    return out


def _product_matches(advisory_product: str, service: str) -> bool:
    a = advisory_product.lower()
    s = (service or "").lower()
    return a in s or s in a


def match_advisories(
    service: str,
    version: Optional[str],
    path: Optional[Path] = None,
) -> List[tuple]:
    """Return ``(advisory, status)`` tuples for a service/version pair.

    ``status`` is one of ``affected``, ``not_affected`` or ``unknown``.
    """
    parsed = parse_version(version)
    results: List[tuple] = []
    for adv in load_advisories(path):
        if not _product_matches(adv.product, service):
            continue
        if parsed is None:
            results.append((adv, "unknown"))
            continue
        in_range = version_in_ranges(parsed, adv.affected)
        if in_range is True:
            results.append((adv, "affected"))
        elif in_range is False:
            results.append((adv, "not_affected"))
        else:
            results.append((adv, "unknown"))
    return results


def advisory_database_available(path: Optional[Path] = None) -> bool:
    p = path or _DATA_FILE
    return p.exists() and bool(load_advisories(p))


__all__ = [
    "Advisory",
    "load_advisories",
    "match_advisories",
    "advisory_database_available",
]
