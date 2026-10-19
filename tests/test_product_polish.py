import asyncio
from html.parser import HTMLParser

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException

from app.main import app, custom_http_exception_handler

client = TestClient(app)


@pytest.mark.parametrize("path", [
    "/lessons/abc", "/quiz/abc", "/flashcards/abc",
    "/admin-duty/dynamic/sessions/invalid",
])
def test_invalid_navigation_identifiers_return_polish_html(path):
    response = client.get(path)
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("text/html")
    assert "nieprawidłowy identyfikator" in response.text
    assert 'href="/lessons"' in response.text
    assert '"detail"' not in response.text


def test_invalid_quiz_post_identifier_returns_html():
    response = client.post("/quiz/abc", data={"question_1": "a"})
    assert response.status_code == 422
    assert "nieprawidłowy identyfikator" in response.text


@pytest.mark.parametrize("path", ["/lessons/999999", "/quiz/999999", "/flashcards/999999", "/missing-page"])
def test_missing_navigation_page_returns_html(path):
    response = client.get(path)
    assert response.status_code == 404
    assert "Nie znaleziono strony" in response.text


def test_api_validation_keeps_exact_json_contract_even_with_html_accept():
    response = client.post(
        "/admin-duty/dynamic/api/command",
        json={"session_id": "invalid", "command": "pwd"},
        headers={"Accept": "text/html"},
    )
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"detail": "Nieprawidłowe dane żądania."}


@pytest.mark.parametrize("path, status, detail", [
    ("/admin-duty/dynamic/api/missing", 404, "Not Found"),
    ("/admin-duty/dynamic/api/start", 405, "Method Not Allowed"),
    ("/api/missing", 404, "Not Found"),
])
def test_api_http_errors_remain_json(path, status, detail):
    response = client.get(path, headers={"Accept": "text/html"})
    assert response.status_code == status
    assert response.json() == {"detail": detail}
    if status == 405:
        assert "POST" in response.headers["allow"]


def test_html_http_error_does_not_render_internal_detail_and_preserves_headers():
    request = Request({
        "type": "http", "method": "GET", "path": "/lessons/1",
        "scheme": "http", "server": ("testserver", 80), "headers": [], "router": app.router,
    })
    response = asyncio.run(custom_http_exception_handler(
        request, HTTPException(503, "<script>internal detail</script>", headers={"Retry-After": "30"}),
    ))
    assert response.status_code == 503
    assert response.headers["retry-after"] == "30"
    assert "Nie udało się otworzyć strony" in response.body.decode()
    assert "internal detail" not in response.body.decode()


class QuizGroups(HTMLParser):
    def __init__(self):
        super().__init__()
        self.groups = []
        self.group = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "fieldset":
            self.group = {"legend": False, "names": set()}
        elif tag == "legend" and self.group is not None:
            self.group["legend"] = True
        elif tag == "input" and attrs.get("type") == "radio":
            assert self.group is not None
            self.group["names"].add(attrs["name"])

    def handle_endtag(self, tag):
        if tag == "fieldset":
            self.groups.append(self.group)
            self.group = None


def test_quiz_answers_have_native_question_groups():
    parser = QuizGroups()
    response = client.get("/quiz/1")
    assert response.status_code == 200
    parser.feed(response.text)
    assert parser.groups
    assert all(group["legend"] and len(group["names"]) == 1 for group in parser.groups)


def test_flashcard_has_keyboard_target_and_accessible_state():
    response = client.get("/flashcards/1")
    assert response.status_code == 200
    assert 'role="button" tabindex="0" aria-pressed="false"' in response.text
    assert 'aria-describedby="flashcard-question"' in response.text
    assert 'class="flashcards-face flashcards-back" aria-hidden="true"' in response.text


def test_lobby_explains_device_and_session_limits_before_generation():
    response = client.get("/admin-duty/dynamic/")
    assert response.status_code == 200
    assert response.text.index('id="desktop-start-notice"') < response.text.index('id="start-easy-button"')
    assert "1024 px" in response.text
    assert "adres URL" in response.text
    assert "45 minutach bezczynności" in response.text
    assert "device.js" in response.text


def test_workspace_explains_resumption_without_indefinite_persistence():
    response = client.get("/admin-duty/dynamic/sessions/12345678-1234-1234-1234-123456789abc")
    assert response.status_code == 200
    assert "ten sam adres URL" in response.text
    assert "45 minutach bezczynności" in response.text
    assert "samo oglądanie mapy nie przedłuża" in response.text
    assert "Wersja mobilna pojawi się" not in response.text
    assert "publiczny snapshot" not in response.text
    assert "POST-INCIDENT REPORT V2" not in response.text
