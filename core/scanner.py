"""
AI Shield - Main scanner engine.

Orchestrates service discovery and security checks. A check that raises is
recorded as an ``error`` check result instead of being silently swallowed,
and the final grade is computed by :func:`core.rating.compute_grade` so that
the CLI, web and report modules never diverge.
"""
from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from core.config import DEFAULT_PORTS
from core.rating import compute_grade
from core.target_policy import TargetDecision, validate_target
from checks import ALL_CHECKS, Finding
from services.detector import identify_service, scan_ports


logger = logging.getLogger("ai-shield.scanner")

_SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization|token|api[-_]?key|password|secret)\s*[:=]\s*[^\s,]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
]


def _sanitize(text: str) -> str:
    out = str(text)
    for pat in _SECRET_PATTERNS:
        out = pat.sub(lambda m: f"{m.group(1)}=***" if m.lastindex else "***", out)
    return out


class ScanResult:
    """Holds the complete result of a scan."""

    def __init__(self, target: str):
        self.id = str(uuid.uuid4())[:8]
        self.target = target
        self.start_time = datetime.now(timezone.utc).isoformat()
        self.end_time: Optional[str] = None
        self.duration = 0
        self.port_data: dict = {}
        self.findings: List[Finding] = []
        self.check_results: Dict[str, str] = {}
        self.grade = "N/A"
        self.risk_score = 0
        self.grade_reasons: List[str] = []

    def calculate_grade(self):
        grade, score, reasons = compute_grade(
            [f.to_dict() for f in self.findings],
            self.check_results,
        )
        self.grade = grade
        self.risk_score = score
        self.grade_reasons = reasons

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "grade": self.grade,
            "risk_score": self.risk_score,
            "grade_reasons": self.grade_reasons,
            "port_data": self.port_data,
            "findings": [f.to_dict() for f in self.findings],
            "check_results": self.check_results,
            "summary": {
                "critical": len([f for f in self.findings if f.severity == "critical"]),
                "high": len([f for f in self.findings if f.severity == "high"]),
                "medium": len([f for f in self.findings if f.severity == "medium"]),
                "low": len([f for f in self.findings if f.severity == "low"]),
                "info": len([f for f in self.findings if f.severity == "info"]),
            },
        }


class Scanner:
    """Main scanner engine."""

    def __init__(self):
        self.history: List[dict] = []
        self.history_file = Path(__file__).parent.parent / "data" / "scan_history.json"
        self._load_history()

    def _load_history(self):
        if self.history_file.exists():
            try:
                self.history = json.loads(self.history_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self.history = []

    def _save_history(self):
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.write_text(
                json.dumps(self.history, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            logger.warning("could not persist scan history", exc_info=True)

    @staticmethod
    def expand_target(target: str) -> List[str]:
        if "/" in target:
            try:
                network = ipaddress.ip_network(target, strict=False)
            except ValueError:
                return [target]
            return [str(ip) for ip in network.hosts()]
        return [target]

    def _resolve_target(self, target: str, allow_private: Optional[bool] = None) -> TargetDecision:
        decision = validate_target(target, allow_private=allow_private)
        if not decision.allowed:
            raise ValueError(decision.reason)
        return decision

    async def run_scan(
        self,
        target: str,
        ports: Optional[List[int]] = None,
        checks: Optional[List[str]] = None,
        progress_callback=None,
        allow_private: Optional[bool] = None,
    ) -> dict:
        """Run a full security scan on a single target."""
        result = ScanResult(target)
        start = time.time()

        decision = self._resolve_target(target, allow_private=allow_private)
        scan_host = decision.scan_target or target

        if ports is None:
            ports = list(DEFAULT_PORTS.keys())
        if checks is None:
            checks = list(ALL_CHECKS.keys())

        if progress_callback:
            await progress_callback("port_scan", "Scanning ports...")

        result.port_data = await scan_ports(scan_host, ports)

        ai_services = [s for s in result.port_data.get("services", []) if s.get("detected")]
        if not ai_services:
            ai_services = [
                s
                for s in result.port_data.get("services", [])
                if s["port"] in result.port_data.get("open_ports", [])
            ]

        for svc in ai_services:
            port = svc["port"]
            service_name = svc.get("service", "Unknown")
            version = svc.get("version")

            if progress_callback:
                await progress_callback("checks", f"Checking {service_name} on port {port}...")

            for check_name in checks:
                check_fn = ALL_CHECKS.get(check_name)
                if check_fn is None:
                    result.check_results[check_name] = "unknown"
                    continue
                try:
                    check_result = await check_fn(scan_host, port, service_name, version)
                except Exception as exc:
                    result.check_results[check_name] = "error"
                    logger.warning(
                        "check %s failed on %s:%s: %s",
                        check_name, scan_host, port, _sanitize(str(exc)),
                    )
                    continue
                result.check_results[check_name] = check_result.status.value
                result.findings.extend(check_result.findings)

        result.end_time = datetime.now(timezone.utc).isoformat()
        result.duration = round(time.time() - start, 2)
        result.calculate_grade()

        result_dict = result.to_dict()
        self.history.insert(0, result_dict)
        self.history = self.history[:50]
        self._save_history()

        return result_dict

    async def run_subnet_scan(
        self,
        target: str,
        ports: Optional[List[int]] = None,
        checks: Optional[List[str]] = None,
        progress_callback=None,
        allow_private: Optional[bool] = None,
    ) -> List[dict]:
        """Run scan on multiple targets (subnet/CIDR)."""
        # Validate the subnet once before expanding.
        self._resolve_target(target, allow_private=allow_private)
        targets = self.expand_target(target)
        results = []
        for i, ip in enumerate(targets):
            if progress_callback:
                await progress_callback("subnet", f"Scanning {ip} ({i + 1}/{len(targets)})...")
            try:
                result = await self.run_scan(ip, ports, checks, allow_private=allow_private)
                results.append(result)
            except Exception as exc:
                results.append({"target": ip, "error": _sanitize(str(exc))})
        return results

    def get_history(self) -> List[dict]:
        return self.history

    def get_scan(self, scan_id: str) -> Optional[dict]:
        for scan in self.history:
            if scan.get("id") == scan_id:
                return scan
        return None


# Global scanner instance (preserved for web API compatibility).
scanner = Scanner()


__all__ = ["Scanner", "ScanResult", "scanner"]
