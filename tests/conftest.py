import os

import httpx
import pytest

os.environ["SHELLFORGE_AI_GENERATION_ENABLED"] = "false"


@pytest.fixture(autouse=True)
def prevent_live_ai_requests(monkeypatch):
    attempted = []
    original = httpx.AsyncHTTPTransport.handle_async_request

    async def guarded(transport, request):
        if request.url.host == "generativelanguage.googleapis.com":
            attempted.append(True)
            raise RuntimeError("Testy wymagają mockowanego transportu AI.")
        return await original(transport, request)

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", guarded)
    yield
    assert not attempted, "Test próbował wykonać prawdziwy request AI."
