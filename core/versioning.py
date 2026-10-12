"""
Version parsing, comparison and range matching.

The previous implementation compared version strings with plain string
comparison, which produces wrong results for anything but fixed-width
numeric versions. This module provides a small, dependency-free parser
that handles common version shapes:

* leading ``v`` / ``V`` prefix
* missing or non-numeric segments (treated as 0)
* pre-release markers (``-rc1``, ``alpha``, ``beta``, ``preview``, ``dev``)
* build metadata after ``+``

Unknown or unparseable versions return ``None`` so callers can report
"unknown" instead of guessing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


_PRE_LABELS = {
    "alpha": "a",
    "a": "a",
    "beta": "b",
    "b": "b",
    "rc": "rc",
    "c": "rc",
    "pre": "rc",
    "preview": "rc",
    "dev": "dev",
}


@dataclass(frozen=True)
class Version:
    release: Tuple[int, ...]
    pre: Optional[Tuple[str, int]] = None

    def __str__(self) -> str:
        base = ".".join(str(x) for x in self.release)
        if self.pre:
            base += f"-{self.pre[0]}{self.pre[1]}"
        return base


def _parse_pre(token: str) -> Optional[Tuple[str, int]]:
    token = token.strip().strip(".")
    if not token:
        return None
    m = re.match(r"(?i)^(alpha|beta|rc|pre|preview|a|b|c|dev)\.?(\d*)$", token)
    if not m:
        return None
    label = _PRE_LABELS.get(m.group(1).lower(), m.group(1).lower())
    num = int(m.group(2)) if m.group(2) else 0
    return (label, num)


def parse_version(text: object) -> Optional[Version]:
    """Parse a version string into a comparable :class:`Version`.

    Returns ``None`` when the input cannot be interpreted as a version.
    """
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return None

    # Drop build metadata.
    s = s.split("+", 1)[0]

    pre: Optional[Tuple[str, int]] = None
    core = s

    if "-" in s:
        core, _, rest = s.partition("-")
        pre = _parse_pre(rest)
    else:
        m = re.search(r"(?i)[.\-]?(alpha|beta|rc|pre|preview|a|b|c|dev)\.?\d*$", core)
        if m:
            pre = _parse_pre(m.group(0))
            core = core[: m.start()].rstrip(".")

    core = core.lstrip("vV")
    release: List[int] = []
    for part in core.split("."):
        m = re.match(r"\d+", part)
        release.append(int(m.group(0)) if m else 0)

    # A version with no numeric content at all is not a version.
    if not release or all(x == 0 for x in release) and not core.strip():
        return None
    if not core.strip():
        return None

    return Version(tuple(release), pre)


def compare(left: Version, right: Version) -> int:
    """Return -1/0/1 for left < / == / > right."""
    a = list(left.release)
    b = list(right.release)
    while len(a) < len(b):
        a.append(0)
    while len(b) < len(a):
        b.append(0)
    for x, y in zip(a, b):
        if x < y:
            return -1
        if x > y:
            return 1

    # Release parts equal; compare pre-release. A version without a
    # pre-release marker is *newer* than a pre-release of the same release.
    if left.pre is None and right.pre is None:
        return 0
    if left.pre is None:
        return 1
    if right.pre is None:
        return -1

    if left.pre[0] < right.pre[0]:
        return -1
    if left.pre[0] > right.pre[0]:
        return 1
    if left.pre[1] < right.pre[1]:
        return -1
    if left.pre[1] > right.pre[1]:
        return 1
    return 0


def _cmp_str(left: str, right: str) -> int:
    a = parse_version(left)
    b = parse_version(right)
    if a is None or b is None:
        return 0
    return compare(a, b)


_RANGE_OPS = {"<", "<=", "==", "=", ">", ">=", "!="}


def version_in_ranges(
    version: Optional[Version],
    ranges: Iterable[str],
) -> Optional[bool]:
    """Return whether *version* matches every range string.

    ``None`` means the result cannot be determined (unparseable version or
    range). Each range is an operator followed by a version, e.g.
    ``"<0.1.34"`` or ``">=0.1.0"``.
    """
    if version is None:
        return None
    range_list = list(ranges)
    if not range_list:
        return None

    for spec in range_list:
        spec = spec.strip()
        m = re.match(r"(<=|>=|==|!=|<|>|=)\s*(.*)$", spec)
        if not m:
            return None
        op, ver_text = m.group(1), m.group(2).strip()
        if op == "=":
            op = "=="
        target = parse_version(ver_text)
        if target is None:
            return None

        c = compare(version, target)
        ok = {
            "<": c < 0,
            "<=": c <= 0,
            "==": c == 0,
            "!=": c != 0,
            ">": c > 0,
            ">=": c >= 0,
        }[op]
        if not ok:
            return False
    return True


def is_older(version: Optional[Version], than: str) -> Optional[bool]:
    """Convenience helper for ``version < than``."""
    if version is None:
        return None
    return version_in_ranges(version, [f"<{than}"])


__all__ = [
    "Version",
    "parse_version",
    "compare",
    "version_in_ranges",
    "is_older",
]
