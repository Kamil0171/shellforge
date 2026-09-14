from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dynamic_lobby_renders_difficulty_selection_and_assets():
    response = client.get("/admin-duty/dynamic/")

    assert response.status_code == 200
    assert "Dynamic Incident Lab" in response.text
    assert 'id="start-easy-button"' in response.text
    assert 'data-difficulty="easy"' in response.text
    assert "Łatwy" in response.text
    assert "Średni" in response.text
    assert "Trudny" in response.text
    assert "Poziom w przygotowaniu" not in response.text
    assert 'id="start-medium-button"' in response.text
    assert 'data-difficulty="medium"' in response.text
    assert 'id="start-hard-button"' in response.text
    assert 'data-difficulty="hard"' in response.text
    assert response.text.count('type="button" disabled') == 0
    assert 'id="generation-overlay"' in response.text
    assert (
        'href="http://testserver/static/admin_duty/dynamic/dynamic.css' in response.text
    )
    assert 'src="http://testserver/static/admin_duty/dynamic/index.js' in response.text
    assert "dynamic.css?v=ai-loading-1" in response.text
    assert "index.js?v=incident-ai-v1" in response.text
    assert "Przygotowywanie incydentu…" in response.text
    assert 'id="generation-status"' in response.text
    assert "generation-progress-bar" not in response.text

    source = client.get("/static/admin_duty/dynamic/index.js")
    assert source.status_code == 200
    assert "window.location.replace(" in source.text
    assert "window.location.assign(" not in source.text


def test_dynamic_workspace_bootstraps_only_session_id_and_frontend_containers():
    session_id = uuid4()

    response = client.get(f"/admin-duty/dynamic/sessions/{session_id}")

    assert response.status_code == 200
    assert f'data-session-id="{session_id}"' in response.text
    assert 'id="terminal-output"' in response.text
    assert 'id="terminal-input"' in response.text
    assert 'id="incident-briefing"' in response.text
    assert 'maxlength="1024"' in response.text
    assert 'id="objectives-list"' in response.text
    assert 'id="completion-overlay"' in response.text
    assert 'id="end-summary"' in response.text
    assert 'id="post-incident-report"' in response.text
    assert "Podsumowanie po incydencie" in response.text
    assert 'id="game-canvas"' in response.text
    assert 'id="desktop-gate"' in response.text
    assert 'id="mission-drawer"' in response.text
    assert 'id="support-overlay"' in response.text
    assert 'id="support-runbooks"' in response.text
    assert 'id="operational-guidance"' in response.text
    assert 'id="exploration-counter"' not in response.text
    assert 'class="game-controls"' not in response.text
    assert 'id="terminal-overlay"' in response.text
    assert 'id="monitoring-overlay"' in response.text
    assert 'id="post-incident-root-chain"' in response.text
    assert 'id="post-incident-partial-explanation"' in response.text
    assert 'id="rack-overlay"' in response.text
    assert 'id="request-hint-button"' in response.text
    assert 'id="exit-session-button"' in response.text
    assert 'id="exit-confirmation"' in response.text
    assert (
        'href="http://testserver/static/admin_duty/dynamic/gameplay.css'
        in response.text
    )
    assert (
        'src="https://cdn.jsdelivr.net/npm/phaser@3.90.0/dist/phaser.min.js"'
        in response.text
    )
    assert 'src="http://testserver/static/admin_duty/dynamic/game.js' in response.text
    assert (
        'src="http://testserver/static/admin_duty/dynamic/terminal.js' in response.text
    )
    assert (
        'src="http://testserver/static/admin_duty/dynamic/scenario.js' in response.text
    )


def test_dynamic_gameplay_assets_include_keyboard_and_overlay_contracts():
    game = client.get("/static/admin_duty/dynamic/game.js")
    terminal = client.get("/static/admin_duty/dynamic/terminal.js")
    scenario = client.get("/static/admin_duty/dynamic/scenario.js")

    assert game.status_code == 200
    assert "Phaser.Input.Keyboard.JustDown" in game.text
    assert "scene.input.keyboard.enabled = !locked" in game.text
    assert "game.canvas.focus({ preventScroll: true })" in game.text
    assert "W.DiscoverySystem" in game.text
    systems = client.get("/static/admin_duty/dynamic/world-systems.js")
    assert "createRadialGradient" in systems.text
    assert "destination-out" in systems.text
    assert terminal.status_code == 200
    assert 'form.addEventListener("submit"' in terminal.text
    assert 'event.key === "Enter"' in terminal.text
    assert '["clear", "cls"]' in terminal.text
    assert "output.replaceChildren()" in terminal.text
    assert 'event.key === "Escape"' in terminal.text
    assert "input.focus({ preventScroll: true })" in terminal.text
    assert scenario.status_code == 200
    assert "window.innerWidth >= 1024" in scenario.text
    assert "navigator.maxTouchPoints" in scenario.text
    assert 'window.scrollTo({ top: 0, left: 0, behavior: "instant" })' in scenario.text
    assert 'window.location.replace("/admin-duty/dynamic/")' in scenario.text
    assert 'link.label === "zależy od"' in scenario.text
    assert "post_incident" in scenario.text


def test_dynamic_workspace_rejects_invalid_uuid():
    response = client.get("/admin-duty/dynamic/sessions/not-a-uuid")

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


def test_admin_duty_lobby_links_only_dynamic_mode():
    response = client.get("/admin-duty/")

    assert response.status_code == 200
    assert 'href="/admin-duty/dynamic/"' in response.text
    assert 'class="back-to-menu duty-back-action"' in response.text
    assert "Wybierz tryb Symulatora" in response.text
    assert "Dynamic Incident Lab" in response.text
    assert "Tryb aktywny" in response.text
    assert "Wiele hostów" in response.text
    assert "Punktacja działań" in response.text
    assert "admin_duty.css?v=lobby-refresh-1" in response.text
    assert "SCENARIUSZ KLASYCZNY" not in response.text
    assert "INC-001" not in response.text
    assert "INC-002" not in response.text
    assert "INC-003" not in response.text
