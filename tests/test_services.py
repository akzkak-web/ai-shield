import asyncio

import httpx

import services.detector as detector_mod


_REAL_ASYNC_CLIENT = httpx.AsyncClient


def _mock_async_client(handler):
    def factory(*args, **kwargs):
        return _REAL_ASYNC_CLIENT(
            transport=httpx.MockTransport(handler),
            base_url="http://unused",
        )

    return factory


def test_identify_service_on_nonstandard_port_by_content(monkeypatch):
    """Ollama on a dynamic Docker-mapped port must still be detected."""

    def handler(request):
        path = request.url.path
        if path == "/api/tags":
            return httpx.Response(200, json={"models": []})
        if path == "/api/version":
            return httpx.Response(200, json={"version": "0.1.33"})
        return httpx.Response(404)

    monkeypatch.setattr(
        detector_mod.httpx,
        "AsyncClient",
        _mock_async_client(handler),
    )

    result = asyncio.run(detector_mod.identify_service("127.0.0.1", 56789))

    assert result is not None
    assert result["service"] == "Ollama"
    assert result["detected"] is True
    assert result["version"] == "0.1.33"


def test_identify_service_returns_none_without_matching_content(monkeypatch):
    def handler(request):
        return httpx.Response(404)

    monkeypatch.setattr(
        detector_mod.httpx,
        "AsyncClient",
        _mock_async_client(handler),
    )

    result = asyncio.run(detector_mod.identify_service("127.0.0.1", 56789))
    assert result is None


def test_identify_service_fixed_port_still_detects_ollama(monkeypatch):
    def handler(request):
        path = request.url.path
        if path == "/api/tags":
            return httpx.Response(200, json={"models": []})
        if path == "/api/version":
            return httpx.Response(200, json={"version": "0.1.33"})
        return httpx.Response(404)

    monkeypatch.setattr(
        detector_mod.httpx,
        "AsyncClient",
        _mock_async_client(handler),
    )

    result = asyncio.run(detector_mod.identify_service("127.0.0.1", 11434))

    assert result is not None
    assert result["service"] == "Ollama"
    assert result["detected"] is True
    assert result["version"] == "0.1.33"


def test_identify_service_does_not_match_models_text_without_json_key(monkeypatch):
    def handler(request):
        if request.url.path == "/api/tags":
            return httpx.Response(
                200,
                text="<html><body>models</body></html>",
                headers={"content-type": "text/html"},
            )
        return httpx.Response(404)

    monkeypatch.setattr(
        detector_mod.httpx,
        "AsyncClient",
        _mock_async_client(handler),
    )

    result = asyncio.run(detector_mod.identify_service("127.0.0.1", 56789))
    assert result is None


def test_identify_service_returns_none_on_connection_error(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("connection failed", request=request)

    monkeypatch.setattr(
        detector_mod.httpx,
        "AsyncClient",
        _mock_async_client(handler),
    )

    result = asyncio.run(detector_mod.identify_service("127.0.0.1", 56789))
    assert result is None
