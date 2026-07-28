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
        "version_path": "/api/version",
        "version_key": "version",
    },
    8000: {
        "name": "vLLM",
        "check_path": "/v1/models",
        "method": "GET",
        "indicator": "data",
        "version_path": "/version",
        "version_key": None,
    },
    8080: {
        "name": "llama.cpp / LocalAI",
        "check_path": "/v1/models",
        "method": "GET",
        "indicator": "data",
        "version_path": None,
        "version_key": None,
    },
    1234: {
        "name": "LM Studio",
        "check_path": "/v1/models",
        "method": "GET",
        "indicator": "data",
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


async def identify_service(host: str, port: int) -> Optional[dict]:
    """Identify AI service running on a port."""
    fp = SERVICE_FINGERPRINTS.get(port)
    if not fp:
        return None

    result = {
        "port": port,
        "service": fp["name"],
        "version": None,
        "detected": False,
        "bind_address": None,
        "response_headers": {},
    }

    try:
        async with httpx.AsyncClient(
            base_url=f"http://{host}:{port}",
            timeout=5.0,
            follow_redirects=False,
        ) as client:
            # Check main endpoint
            try:
                resp = await client.get(fp["check_path"])
                if fp["indicator"] in resp.text.lower():
                    result["detected"] = True
                    result["response_headers"] = dict(resp.headers)
            except Exception:
                pass

            # Try to get version
            if fp.get("version_path"):
                try:
                    resp = await client.get(fp["version_path"])
                    if resp.status_code == 200:
                        data = resp.json()
                        if fp.get("version_key"):
                            result["version"] = data.get(fp["version_key"])
                        elif "version" in data:
                            result["version"] = data.get("version")
                except Exception:
                    pass

            # Check bind address by looking at server header or trying external access
            server = resp.headers.get("server", "") if resp else ""
            if server:
                result["response_headers"]["server"] = server

    except Exception:
        pass

    return result if result["detected"] else None


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
