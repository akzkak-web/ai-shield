"""Fixtures for real-service integration tests.

These tests require Docker and the ``ollama/ollama`` image. They bind only to
loopback, use a unique container name, and tear down ONLY the container they
create (never touching pre-existing containers/images/volumes).
"""
from __future__ import annotations

import shutil
import socket
import subprocess
import time
import uuid

import pytest


DOCKER = shutil.which("docker")
OLLAMA_IMAGE = "ollama/ollama:latest"


def _free_port() -> int:
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait_ready(port: int, timeout: float = 120.0) -> bool:
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/version", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


@pytest.fixture(scope="session")
def ollama():
    """Start a loopback-bound Ollama container and yield {host, port, name}."""
    if DOCKER is None:
        pytest.skip("docker is not available")

    name = f"ai-shield-it-{uuid.uuid4().hex[:8]}"
    port = _free_port()
    subprocess.run(
        [
            DOCKER, "run", "-d", "--name", name,
            "-p", f"127.0.0.1:{port}:11434",
            OLLAMA_IMAGE,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    if not _wait_ready(port):
        subprocess.run([DOCKER, "rm", "-f", name], capture_output=True)
        pytest.fail("Ollama container did not become ready in time")
    try:
        yield {"host": "127.0.0.1", "port": port, "name": name}
    finally:
        # Remove only the container this fixture created.
        subprocess.run([DOCKER, "rm", "-f", name], capture_output=True)
