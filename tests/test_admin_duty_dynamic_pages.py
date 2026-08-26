from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dynamic_lobby_renders_difficulty_selection_and_assets():
    response = client.get("/admin-duty/dynamic/")

    assert response.status_code == 200
    assert "Dynamic Incident Lab" in response.text
    assert 'id="start-easy-button"' in response.text
    assert "Łatwy" in response.text
    assert "Średni" in response.text
    assert "Trudny" in response.text
    assert response.text.count("Poziom w przygotowaniu") == 2
    assert 'id="generation-overlay"' in response.text
    assert (
        'href="http://testserver/static/admin_duty/dynamic/dynamic.css'
        in response.text
    )
    assert (
        'src="http://testserver/static/admin_duty/dynamic/index.js'
        in response.text
    )


def test_dynamic_workspace_bootstraps_only_session_id_and_frontend_containers():
    session_id = uuid4()

    response = client.get(
        f"/admin-duty/dynamic/sessions/{session_id}"
    )

    assert response.status_code == 200
    assert f'data-session-id="{session_id}"' in response.text
    assert 'id="terminal-output"' in response.text
    assert 'id="terminal-input"' in response.text
    assert 'id="incident-briefing"' in response.text
    assert 'maxlength="1024"' in response.text
    assert 'id="objectives-list"' in response.text
    assert 'id="completion-overlay"' in response.text
    assert 'id="end-summary"' in response.text
    assert (
        'src="http://testserver/static/admin_duty/dynamic/scenario.js'
        in response.text
    )


def test_dynamic_workspace_rejects_invalid_uuid():
    response = client.get(
        "/admin-duty/dynamic/sessions/not-a-uuid"
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Nieprawidłowe dane żądania."}


def test_dynamic_pages_do_not_embed_backend_only_incident_data():
    session_id = uuid4()
    responses = (
        client.get("/admin-duty/dynamic/"),
        client.get(f"/admin-duty/dynamic/sessions/{session_id}"),
    )
    forbidden_values = (
        "initial_world_state",
        "completion_condition",
        "fault_type",
        "generation_metadata",
        "systemd.status",
        "systemd.restart",
    )

    for response in responses:
        assert response.status_code == 200

        for value in forbidden_values:
            assert value not in response.text


def test_admin_duty_lobby_links_dynamic_and_classic_modes():
    response = client.get("/admin-duty/")

    assert response.status_code == 200
    assert 'href="/admin-duty/dynamic/"' in response.text
    assert "Dynamic Incident Lab" in response.text
    assert "SCENARIUSZ KLASYCZNY" in response.text
    assert "INC-001" in response.text
    assert 'data-scenario-id="INC-001"' in response.text
    assert "INC-002" not in response.text
    assert "INC-003" not in response.text
