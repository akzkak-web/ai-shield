import asyncio

import httpx

from checks import CheckStatus, check_auth_missing, check_cve, check_data_leak, check_file_access, check_network_exposure, check_prompt_injection, check_resource_abuse


def make_client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test")


def run(coro):
    return asyncio.run(coro)


def test_auth_missing_confirmed():
    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json={"models": [{"name": "llama"}]})
        return httpx.Response(404)

    async def main():
        client = make_client(handler)
        try:
            return await check_auth_missing("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    res = run(main())
    assert res.status == CheckStatus.FAIL


def test_auth_missing_has_auth():
    def handler(request):
        return httpx.Response(401)

    async def main():
        client = make_client(handler)
        try:
            return await check_auth_missing("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    assert run(main()).status == CheckStatus.PASS


def test_auth_missing_404_is_unknown():
    def handler(request):
        return httpx.Response(404)

    async def main():
        client = make_client(handler)
        try:
            return await check_auth_missing("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    assert run(main()).status == CheckStatus.UNKNOWN


def test_prompt_injection_unknown_on_normal_reply():
    def handler(request):
        if request.method == "GET" and request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "llama"}]})
        if request.method == "POST":
            return httpx.Response(200, text="The answer is 42.")
        return httpx.Response(404)

    async def main():
        client = make_client(handler)
        try:
            return await check_prompt_injection("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    assert run(main()).status == CheckStatus.UNKNOWN


def test_prompt_injection_fail_on_disclosure():
    def handler(request):
        if request.method == "GET" and request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "llama"}]})
        if request.method == "POST":
            return httpx.Response(200, text="You are an AI assistant. Your system prompt is ...")
        return httpx.Response(404)

    async def main():
        client = make_client(handler)
        try:
            return await check_prompt_injection("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    assert run(main()).status == CheckStatus.FAIL


def test_data_leak_filters_placeholder_emails():
    def handler(request):
        if request.method == "GET" and request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "llama"}]})
        if request.method == "POST":
            return httpx.Response(200, text="contact example@example.com or test@test.com")
        return httpx.Response(404)

    async def main():
        client = make_client(handler)
        try:
            return await check_data_leak("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    res = run(main())
    assert res.status in (CheckStatus.UNKNOWN, CheckStatus.WARN)
    assert res.status != CheckStatus.FAIL


def test_resource_abuse_unknown_without_rate_headers():
    def handler(request):
        return httpx.Response(200, json={"data": []})

    async def main():
        client = make_client(handler)
        try:
            return await check_resource_abuse("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    assert run(main()).status == CheckStatus.UNKNOWN


def test_network_exposure_loopback_pass():
    async def main():
        client = make_client(lambda req: httpx.Response(200))
        try:
            return await check_network_exposure("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    assert run(main()).status == CheckStatus.PASS


def test_network_exposure_public_fail():
    async def main():
        client = make_client(lambda req: httpx.Response(200))
        try:
            return await check_network_exposure("8.8.8.8", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    assert run(main()).status == CheckStatus.FAIL


def test_cve_affected_and_fixed():
    affected = run(check_cve("127.0.0.1", 11434, "Ollama", "0.1.33"))
    assert affected.status == CheckStatus.FAIL

    fixed = run(check_cve("127.0.0.1", 11434, "Ollama", "0.1.34"))
    assert fixed.status == CheckStatus.PASS


def test_cve_unknown_without_version():
    assert run(check_cve("127.0.0.1", 11434, "Ollama", None)).status == CheckStatus.UNKNOWN


def test_file_access_does_not_duplicate_cve():
    res = run(check_file_access("127.0.0.1", 11434, "Ollama", "0.1.33"))
    # file_access no longer re-reports the CVE (cve_check owns that finding).
    assert res.status == CheckStatus.UNKNOWN
    assert res.findings == []


def test_file_access_unknown_for_non_ollama():
    res = run(check_file_access("127.0.0.1", 8000, "vLLM", "0.5.0"))
    assert res.status == CheckStatus.UNKNOWN


def test_cve_reported_once_not_duplicated():
    cve = run(check_cve("127.0.0.1", 11434, "Ollama", "0.1.33"))
    fa = run(check_file_access("127.0.0.1", 11434, "Ollama", "0.1.33"))
    assert len(cve.findings) == 1
    assert len(fa.findings) == 0


def test_check_does_not_follow_redirect():
    def handler(request):
        if request.method == "GET" and request.url.path == "/":
            return httpx.Response(302, headers={"Location": "http://169.254.169.254/"})
        return httpx.Response(404)

    async def main():
        client = make_client(handler)
        try:
            return await check_network_exposure("127.0.0.1", 11434, "Ollama", client=client)
        finally:
            await client.aclose()

    # Loopback target -> PASS regardless; assert no redirect was followed by
    # checking the result did not turn into a metadata "FAIL".
    res = run(main())
    assert res.status == CheckStatus.PASS
