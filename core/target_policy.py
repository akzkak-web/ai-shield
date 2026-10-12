"""
Target access policy for the scanner.

This is the single source of truth for deciding which scan targets are
acceptable. It exists to prevent the scanner (and, in particular, the web
API) from being used as an SSRF / internal-port-scan primitive.

Policy (default-deny):

* Loopback addresses are always allowed.
* Private / LAN addresses require ``AI_SHIELD_ALLOW_PRIVATE=true`` or an
  explicit entry in ``AI_SHIELD_ALLOWED_TARGETS``.
* Public internet addresses require an explicit entry in
  ``AI_SHIELD_ALLOWED_TARGETS``.
* Cloud metadata (169.254.169.254), link-local, multicast, broadcast,
  unspecified and other non-global reserved ranges are always rejected.
* Hostnames are resolved and every resolved address must be allowed
  (basic DNS-rebinding guard at the validation stage).

The scanner pins the validated address for the actual connection so the
hostname is not re-resolved mid-scan.
"""
from __future__ import annotations

import ipaddress
import os
import socket
from dataclasses import dataclass
from typing import List, Optional, Tuple


class TargetPolicyError(ValueError):
    """Raised when a target is rejected by policy."""


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str) -> List[str]:
    raw = os.environ.get(name, "")
    return [x.strip() for x in raw.split(",") if x.strip()]


def classify_ip(ip: object) -> str:
    """Classify an IP address into a policy-relevant category."""
    addr = ipaddress.ip_address(str(ip))
    if addr.is_loopback:
        return "loopback"
    if addr.is_link_local:
        return "link_local"
    if addr.is_multicast:
        return "multicast"
    if addr.is_unspecified:
        return "unspecified"
    if addr.is_private:
        return "private"
    if addr.version == 6 and addr.ipv4_mapped is not None:
        return classify_ip(addr.ipv4_mapped)
    # Cloud metadata and other special ranges.
    if addr.version == 4 and str(addr).startswith("169.254."):
        return "link_local"
    if addr.version == 4 and str(addr) in ("255.255.255.255",):
        return "broadcast"
    return "public"


_ALWAYS_REJECT = {
    "link_local",
    "multicast",
    "unspecified",
    "broadcast",
}


def _resolve(host: str) -> List[str]:
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise TargetPolicyError(f"cannot resolve target: {host}") from exc
    out: List[str] = []
    for family, _type, _proto, _canon, sockaddr in infos:
        ip = sockaddr[0]
        if ip not in out:
            out.append(ip)
    if not out:
        raise TargetPolicyError(f"target resolved to no addresses: {host}")
    return out


def _allowed_address(ip: str, allow_private: bool, allowed: set[str]) -> bool:
    category = classify_ip(ip)
    if category in _ALWAYS_REJECT:
        return False
    if category == "loopback":
        return True
    if category == "private":
        return allow_private or ip in allowed
    # public
    return ip in allowed


@dataclass
class TargetDecision:
    allowed: bool
    reason: str
    resolved: Optional[List[str]] = None
    scan_target: Optional[str] = None


def validate_target(
    target: str,
    allow_private: Optional[bool] = None,
    allowed_targets: Optional[List[str]] = None,
) -> TargetDecision:
    """Validate a single host/ip (or CIDR) against the target policy."""
    target = (target or "").strip()
    if not target:
        return TargetDecision(False, "empty target")

    # Reject anything that looks like a URL with a scheme.
    if "://" in target:
        return TargetDecision(False, "targets must be host/IP/CIDR, not URLs")

    if allow_private is None:
        allow_private = _env_flag("AI_SHIELD_ALLOW_PRIVATE")
    if allowed_targets is None:
        allowed_targets = _env_list("AI_SHIELD_ALLOWED_TARGETS")
    allowed = set(allowed_targets)

    # CIDR (subnet) is only supported for private ranges and still must be
    # explicitly allowed when it is not loopback.
    if "/" in target:
        try:
            net = ipaddress.ip_network(target, strict=False)
        except ValueError as exc:
            return TargetDecision(False, f"invalid CIDR: {exc}")
        first = classify_ip(net.network_address)
        if first == "loopback":
            return TargetDecision(True, "loopback subnet", resolved=[str(net)])
        if first != "private":
            return TargetDecision(False, "only private subnets may be scanned")
        if not allow_private:
            return TargetDecision(
                False, "private subnet requires AI_SHIELD_ALLOW_PRIVATE=true"
            )
        return TargetDecision(True, "private subnet", resolved=[str(net)])

    # Direct IP literal.
    try:
        ip = ipaddress.ip_address(target)
    except ValueError:
        ip = None

    if ip is not None:
        category = classify_ip(ip)
        if category in _ALWAYS_REJECT:
            return TargetDecision(False, f"address category rejected: {category}")
        if category == "loopback":
            return TargetDecision(True, "loopback", resolved=[str(ip)], scan_target=str(ip))
        if category == "private":
            if allow_private or str(ip) in allowed:
                return TargetDecision(True, "private", resolved=[str(ip)], scan_target=str(ip))
            return TargetDecision(False, "private target not authorized")
        if str(ip) in allowed:
            return TargetDecision(True, "explicitly allowed", resolved=[str(ip)], scan_target=str(ip))
        return TargetDecision(False, "public target not authorized")

    # Hostname: resolve and require every address to be allowed.
    try:
        resolved = _resolve(target)
    except TargetPolicyError as exc:
        return TargetDecision(False, str(exc))

    for r in resolved:
        if not _allowed_address(r, allow_private, allowed):
            return TargetDecision(
                False, f"resolved address {r} is not authorized (DNS-rebinding guard)"
            )

    # Pin the first allowed address so callers connect to it directly.
    return TargetDecision(True, "hostname resolved and authorized", resolved=resolved, scan_target=resolved[0])


def is_loopback_target(host: str) -> bool:
    """True when *host* is unambiguously a loopback literal."""
    try:
        return ipaddress.ip_address(str(host).strip()).is_loopback
    except ValueError:
        return False


__all__ = [
    "TargetPolicyError",
    "TargetDecision",
    "validate_target",
    "classify_ip",
    "is_loopback_target",
]
