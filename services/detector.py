"""
AI Shield - Service Detection Module
Identifies AI services by port/banner/response fingerprinting.
"""
import socket
import asyncio
import httpx
from typing import Optional, List, Dict

# Service fingerprints: (port, path, expected_response_pattern, service_name)
SERVICE_FINGERPRINTS = {
    11434: {
        "name": "Ollama",
        "check_path": "/api/tags",
        "method": "GET",
        "indicator": "models",
        "json_key": "models",
        "version_path": "/api/version",
        "version_key": "version",
    },
    8000: {
        "name": "vLLM",
        "check_path": "/v1/models",
        "method": "GET",
        "indicator": "data",
        "json_key": "data",
        "version_path": "/version",
        "version_key": None,
    },
    8080: {
        "name": "llama.cpp / LocalAI",
        "check_path": "/v1/models",
        "method": "GET",
        "indicator": "data",
        "json_key": "data",
        "version_path": None,
        "version_key": None,
    },
    1234: {
        "name": "LM Studio",
        "check_path": "/v1/models",
        "method": "GET",
        "indicator": "data",
        "json_key": "data",
        "version_path": None,
        "version_key": None,
    },
    3000: {
        "name": "Open WebUI",
        "check_path": "/",
        "method": "GET",
        "indicator": "open-webui",
        "version_path": None,
        "version_key": None,
    },
    7860: {
        "name": "Text-Generation-WebUI",
        "check_path": "/",
        "method": "GET",
        "indicator": "text-generation",
        "version_path": None,
        "version_key": None,
    },
    5000: {
        "name": "LocalAI",
        "check_path": "/v1/models",
        "method": "GET",
        "indicator": "data",
        "json_key": "data",
        "version_path": None,
        "version_key": None,
    },
}


async def check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a TCP port is open."""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return False


def _response_matches(resp, candidate: dict) -> bool:
    """Return True only when the response supports the service fingerprint.

    For JSON endpoints we require the expected key at the top level instead of
    merely searching arbitrary text. This prevents a generic page that happens
    to contain the word ``models`` or ``data`` from being misidentified as an
    AI service on a non-standard port.
    """
    json_key = candidate.get("json_key")
    if json_key:
        try:
            data = resp.json()
        except Exception:
            return False
        return isinstance(data, dict) and json_key in data
    return candidate["indicator"] in resp.text.lower()


async def identify_service(host: str, port: int) -> Optional[dict]:
    """Identify AI service running on a port."""
    fp = SERVICE_FINGERPRINTS.get(port)
    # Fixed-port fingerprints are authoritative for their configured port.
    # For non-standard ports (for example Docker port mappings), fall back to
    # content-based identification so a service is not silently reported as
    # "Unknown" merely because it is reachable on a random local port.
    candidates = [fp] if fp is not None else list(SERVICE_FINGERPRINTS.values())

    async with httpx.AsyncClient(
        base_url=f"http://{host}:{port}",
        timeout=5.0,
        follow_redirects=False,
    ) as client:
        for candidate in candidates:
            if candidate is None:
                continue
            result = {
                "port": port,
                "service": candidate["name"],
                "version": None,
                "detected": False,
                "bind_address": None,
                "response_headers": {},
            }
            try:
                resp = await client.get(candidate["check_path"])
            except Exception:
                continue

            result["response_headers"] = dict(resp.headers)
            if not _response_matches(resp, candidate):
                continue

            result["detected"] = True

            # Only fetch version once a service has actually been detected.
            if candidate.get("version_path"):
                try:
                    vr = await client.get(candidate["version_path"])
                    if vr.status_code == 200:
                        data = vr.json()
                        if isinstance(data, dict):
                            if candidate.get("version_key"):
                                result["version"] = data.get(candidate["version_key"])
                            elif "version" in data:
                                result["version"] = data.get("version")
                except Exception:
                    pass
            return result

    return None


async def scan_ports(host: str, ports: List[int], timeout: float = 2.0) -> Dict:
    """Scan multiple ports and return open ports with service info."""
    tasks = [check_port(host, p, timeout) for p in ports]
    results = await asyncio.gather(*tasks)

    open_ports = [p for p, is_open in zip(ports, results) if is_open]

    # Identify services on open ports
    services = []
    for port in open_ports:
        svc = await identify_service(host, port)
        if svc:
            services.append(svc)
        else:
            services.append({
                "port": port,
                "service": "Unknown",
                "version": None,
                "detected": False,
            })

    return {
        "host": host,
        "total_scanned": len(ports),
        "open_ports": open_ports,
        "services": services,
    }
