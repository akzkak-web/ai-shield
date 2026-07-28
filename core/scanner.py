"""
AI Shield - Main Scanner Engine
Orchestrates service discovery and security checks.
"""
import asyncio
import time
import uuid
import json
import ipaddress
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from services.detector import scan_ports, identify_service
from core.config import DEFAULT_PORTS
from checks import ALL_CHECKS, Finding
from core.config import SEVERITY


class ScanResult:
    """Holds the complete result of a scan."""

    def __init__(self, target: str):
        self.id = str(uuid.uuid4())[:8]
        self.target = target
        self.start_time = datetime.utcnow().isoformat()
        self.end_time = None
        self.duration = 0
        self.port_data = {}
        self.findings: List[Finding] = []
        self.grade = "N/A"
        self.risk_score = 0

    def calculate_grade(self):
        """Calculate security grade based on findings."""
        if not self.findings:
            self.grade = "A"
            self.risk_score = 0
            return

        total_weight = sum(SEVERITY.get(f.severity, {}).get("weight", 0) for f in self.findings)
        self.risk_score = min(total_weight, 100)

        if self.risk_score >= 60:
            self.grade = "F"
        elif self.risk_score >= 40:
            self.grade = "D"
        elif self.risk_score >= 25:
            self.grade = "C"
        elif self.risk_score >= 10:
            self.grade = "B"
        else:
            self.grade = "A"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "grade": self.grade,
            "risk_score": self.risk_score,
            "port_data": self.port_data,
            "findings": [f.to_dict() for f in self.findings],
            "summary": {
                "critical": len([f for f in self.findings if f.severity == "critical"]),
                "high": len([f for f in self.findings if f.severity == "high"]),
                "medium": len([f for f in self.findings if f.severity == "medium"]),
                "low": len([f for f in self.findings if f.severity == "low"]),
                "info": len([f for f in self.findings if f.severity == "info"]),
            }
        }


class Scanner:
    """Main scanner engine."""

    def __init__(self):
        self.history: List[dict] = []
        self.history_file = Path(__file__).parent.parent / "data" / "scan_history.json"
        self._load_history()

    def _load_history(self):
        """Load scan history from file."""
        if self.history_file.exists():
            try:
                self.history = json.loads(self.history_file.read_text())
            except Exception:
                self.history = []

    def _save_history(self):
        """Save scan history to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(json.dumps(self.history, ensure_ascii=False, indent=2))

    @staticmethod
    def expand_target(target: str) -> List[str]:
        """Expand target to list of IPs. Supports CIDR notation."""
        try:
            # Check if it's a CIDR network
            if "/" in target:
                network = ipaddress.ip_network(target, strict=False)
                return [str(ip) for ip in network.hosts()]
            else:
                # Single IP or hostname
                return [target]
        except ValueError:
            # Not a valid IP/CIDR, treat as hostname
            return [target]

    async def run_scan(
        self,
        target: str,
        ports: Optional[List[int]] = None,
        checks: Optional[List[str]] = None,
        progress_callback=None,
    ) -> dict:
        """Run a full security scan on a single target."""
        result = ScanResult(target)
        start = time.time()

        # Default ports
        if ports is None:
            ports = list(DEFAULT_PORTS.keys())

        # Default checks (all)
        if checks is None:
            checks = list(ALL_CHECKS.keys())

        # Phase 1: Port scanning
        if progress_callback:
            await progress_callback("port_scan", "Scanning ports...")

        result.port_data = await scan_ports(target, ports)

        # Phase 2: Security checks on detected services
        ai_services = [s for s in result.port_data.get("services", []) if s.get("detected")]

        if not ai_services:
            # Still check open ports for unknown services
            ai_services = [s for s in result.port_data.get("services", []) if s["port"] in result.port_data["open_ports"]]

        for i, svc in enumerate(ai_services):
            port = svc["port"]
            service_name = svc.get("service", "Unknown")
            version = svc.get("version")

            if progress_callback:
                await progress_callback("checks", f"Checking {service_name} on port {port}...")

            for check_name in checks:
                check_fn = ALL_CHECKS.get(check_name)
                if not check_fn:
                    continue

                try:
                    if check_name == "cve_check":
                        findings = await check_fn(target, port, service_name, version)
                    else:
                        findings = await check_fn(target, port, service_name)
                    result.findings.extend(findings)
                except Exception as e:
                    pass

        # Finalize
        result.end_time = datetime.utcnow().isoformat()
        result.duration = round(time.time() - start, 2)
        result.calculate_grade()

        result_dict = result.to_dict()
        self.history.insert(0, result_dict)
        self.history = self.history[:50]  # Keep last 50 scans
        self._save_history()

        return result_dict

    async def run_subnet_scan(
        self,
        target: str,
        ports: Optional[List[int]] = None,
        checks: Optional[List[str]] = None,
        progress_callback=None,
    ) -> List[dict]:
        """Run scan on multiple targets (subnet/CIDR)."""
        targets = self.expand_target(target)
        results = []

        for i, ip in enumerate(targets):
            if progress_callback:
                await progress_callback("subnet", f"Scanning {ip} ({i+1}/{len(targets)})...")

            try:
                result = await self.run_scan(ip, ports, checks)
                results.append(result)
            except Exception as e:
                results.append({"target": ip, "error": str(e)})

        return results

    def get_history(self) -> List[dict]:
        return self.history

    def get_scan(self, scan_id: str) -> Optional[dict]:
        for scan in self.history:
            if scan["id"] == scan_id:
                return scan
        return None


# Global scanner instance
scanner = Scanner()
