#!/usr/bin/env python3
"""Local isolated mock Ollama for demos and offline sample reports.

Read-only endpoints only, binds 127.0.0.1 by default. This is NOT a real
Ollama server: it exists so the CLI can be demonstrated end to end in an
isolated test environment without requiring Ollama or Docker.
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MockOllamaHandler(BaseHTTPRequestHandler):
    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/version":
            return self._json({"version": "0.1.33"})
        if self.path == "/api/tags":
            return self._json({"models": [{"name": "demo:latest"}]})
        if self.path == "/v1/models":
            return self._json(
                {"object": "list", "data": [{"id": "demo:latest"}]}
            )
        if self.path == "/":
            return self._json({"ok": True})
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):  # silence per-request logs
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18099)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MockOllamaHandler)
    print(
        f"Mock Ollama listening on http://{args.host}:{args.port} "
        "(demo only, not a real Ollama)"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
