from datetime import UTC, datetime, timedelta

import pytest

from app.admin_duty.components.scenarios import build_hard_draft, build_medium_draft
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.generation import convert_draft_to_definition
from app.admin_duty.domain.reporting import (
    CommandClassification,
    build_post_incident_analysis,
)
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    InMemoryScenarioRepository,
    InMemorySessionRepository,
)
from app.admin_duty.services import DynamicIncidentService

NOW = datetime(2026, 9, 14, 15, 0, tzinfo=UTC)


def _service_for(definition):
    scenarios = InMemoryScenarioRepository()
    sessions = InMemorySessionRepository()
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(),
        scenario_repository=scenarios,
        session_repository=sessions,
    )
    started = service._start_definition(definition, NOW)
    return service, sessions, started


def _complete(definition, *, prefix=()):
    service, sessions, started = _service_for(definition)
    current = NOW
    for command in prefix:
        current += timedelta(seconds=1)
        service.execute_command(started.session_id, command, now=current)
    for step in definition.solution:
        current += timedelta(seconds=2)
        result = service.execute_command(started.session_id, step.input, now=current)
        if step.capability_id == "filesystem.edit":
            content = {field.key: field.value for field in step.parameters}["content"]
            current += timedelta(seconds=1)
            service.save_file(
                started.session_id,
                path=result.editor.path,
                content=content,
                now=current,
            )
    view = service.get_progress(started.session_id, now=current)
    return view.post_incident, sessions.get(started.session_id, now=current)


def test_command_history_keeps_minimal_structured_context_in_order():
    definition = convert_draft_to_definition(
        build_medium_draft("dependency-firewall-blocked", seed=21),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    commands = DynamicCommandService()
    commands.execute(
        definition,
        state,
        "ssh data-01",
        now=NOW + timedelta(seconds=1),
    )
    commands.execute(
        definition,
        state,
        "firewall-cmd --list-all",
        now=NOW + timedelta(seconds=2),
    )

    assert [record.order for record in state.command_history] == [1, 2]
    assert state.command_history[0].host_id == "host-edge-01"
    assert state.command_history[1].host_id == "host-data-01"
    assert state.command_history[1].capability_id == "firewalld.command"
    assert state.command_history[1].arguments == ("--list-all",)
    assert state.command_history[1].success is True
    serialized = str(
        [record.model_dump(mode="json") for record in state.command_history]
    ).casefold()
    for forbidden in ("terminal output", "raw_response", "provider", "model", "authorization"):
        assert forbidden not in serialized


def test_saved_file_content_is_not_stored_in_command_history():
    generator = DeterministicIncidentGenerator()
    definition = next(
        candidate
        for seed in range(100)
        if (
            candidate := generator.generate(
                DifficultyLevel.EASY, seed=seed, now=NOW
            )
        ).faults[0].fault_type
        == "systemd_wrong_exec_start"
    )
    state = create_session_runtime(definition, now=NOW)
    commands = DynamicCommandService()
    editor = commands.execute(
        definition,
        state,
        definition.solution[2].input,
        now=NOW + timedelta(seconds=1),
    ).editor
    commands.save_file(
        definition,
        state,
        path=editor.path,
        content="TAJNA_TRESC_PLIKU",
        now=NOW + timedelta(seconds=2),
    )

    history = str([record.model_dump(mode="json") for record in state.command_history])
    assert "TAJNA_TRESC_PLIKU" not in history
    assert state.command_history[-1].environment_changed is True


def test_classifier_uses_structured_capability_instead_of_command_substrings():
    definition = convert_draft_to_definition(
        build_medium_draft("dependency-firewall-blocked", seed=21),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    commands = DynamicCommandService()
    commands.execute(
        definition,
        state,
        "cat /etc/systemd/system/orders-api.service",
        now=NOW + timedelta(seconds=1),
    )
    analysis = build_post_incident_analysis(definition, state)

    assert analysis.command_review[0].classification is CommandClassification.UNNECESSARY


@pytest.mark.parametrize(
    ("category", "host", "inspection", "repair"),
    (
        (
            "dependency-firewall-blocked",
            "data-01",
            "firewall-cmd --list-all",
            "firewall-cmd --permanent --add-port=5432/tcp",
        ),
        (
            "networkmanager-dns-invalid",
            "app-01",
            "nmcli connection show",
            "nmcli connection modify System-ens192 ipv4.dns 10.24.8.53",
        ),
        (
            "dependency-package-missing",
            "app-01",
            "dnf info python3-psycopg2",
            "dnf install python3-psycopg2",
        ),
    ),
)
def test_compound_capabilities_distinguish_inspection_from_mutation(
    category, host, inspection, repair
):
    definition = convert_draft_to_definition(
        build_medium_draft(category, seed=21), created_at=NOW
    )
    state = create_session_runtime(definition, now=NOW)
    commands = DynamicCommandService()
    commands.execute(definition, state, f"ssh {host}", now=NOW + timedelta(seconds=1))
    commands.execute(definition, state, inspection, now=NOW + timedelta(seconds=2))
    commands.execute(definition, state, repair, now=NOW + timedelta(seconds=3))
    review = build_post_incident_analysis(definition, state).command_review

    assert review[-2].classification is CommandClassification.DIAGNOSTIC
    assert review[-1].classification is CommandClassification.REPAIR


def test_incident_relevance_rejects_unrelated_repair_target():
    definition = convert_draft_to_definition(
        build_medium_draft("dependency-package-missing", seed=21),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    commands = DynamicCommandService()
    commands.execute(
        definition, state, "ssh app-01", now=NOW + timedelta(seconds=1)
    )
    commands.execute(
        definition,
        state,
        "dnf install nginx",
        now=NOW + timedelta(seconds=2),
    )
    item = build_post_incident_analysis(definition, state).command_review[-1]

    assert item.classification is CommandClassification.UNNECESSARY
    assert item.relevance.value == "unrelated"


def test_status_and_journal_change_from_diagnosis_to_post_repair_verification():
    definition = convert_draft_to_definition(
        build_medium_draft("dependency-package-missing", seed=21),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    commands = DynamicCommandService()
    sequence = (
        "ssh app-01",
        "systemctl status orders-api",
        "journalctl -u orders-api",
        "dnf install python3-psycopg2",
        "systemctl restart orders-api",
        "systemctl status orders-api",
    )
    for index, command in enumerate(sequence, 1):
        commands.execute(
            definition, state, command, now=NOW + timedelta(seconds=index)
        )
    review = build_post_incident_analysis(definition, state).command_review

    assert review[1].classification is CommandClassification.DIAGNOSTIC
    assert review[2].classification is CommandClassification.DIAGNOSTIC
    assert review[-1].classification is CommandClassification.VERIFICATION


def test_hard_command_review_covers_every_classification_and_relevance():
    definition = convert_draft_to_definition(
        build_hard_draft("H-01", seed=23), created_at=NOW
    )
    report, _ = _complete(definition, prefix=("pwd", "uptime"))

    classifications = {item.classification for item in report.command_review}
    assert classifications == set(CommandClassification)
    assert any(item.relevance.value == "direct" for item in report.command_review)
    assert any(item.relevance.value == "unrelated" for item in report.command_review)
    assert report.efficiency.commands_total == len(report.command_review)
    assert report.efficiency.useful_commands == (
        report.efficiency.diagnostic_commands
        + report.efficiency.repair_commands
        + report.efficiency.verification_commands
    )


def test_efficiency_handles_empty_history_without_division_by_zero():
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, seed=3, now=NOW
    )
    state = create_session_runtime(definition, now=NOW)
    efficiency = build_post_incident_analysis(definition, state).efficiency

    assert efficiency.commands_total == 0
    assert efficiency.useful_commands == 0
    assert efficiency.diagnostic_efficiency is None
    assert efficiency.time_to_resolve_seconds is None


def test_easy_report_is_compact_and_has_learning_material():
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, seed=3, now=NOW
    )
    report, _ = _complete(definition)

    assert report.version == "2.0"
    assert report.incident_summary and report.root_cause
    assert report.root_cause_chain == ()
    assert report.primary_fault is None
    assert 2 <= len(report.key_signals) <= 3
    assert 2 <= len(report.learning_points) <= 5
    assert 2 <= len(report.real_world_takeaways) <= 4
    assert report.score >= 0


def test_medium_report_contains_dependency_impact_efficiency_and_hints():
    definition = convert_draft_to_definition(
        build_medium_draft("dependency-package-missing", seed=31),
        created_at=NOW,
    )
    report, _ = _complete(definition)

    assert len(report.impact_path) >= 3
    assert report.efficiency.commands_total == len(report.commands_used)
    assert report.efficiency.diagnostic_efficiency is not None
    assert report.hints_used == 0
    assert report.hint_cost == 0
    assert report.command_review
    assert report.real_world_takeaways


def test_report_reuses_existing_hint_cost_and_final_score():
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, seed=3, now=NOW
    )
    service, sessions, started = _service_for(definition)
    service.request_hint(started.session_id, now=NOW + timedelta(seconds=1))
    current = NOW + timedelta(seconds=1)
    for step in definition.solution:
        current += timedelta(seconds=2)
        result = service.execute_command(started.session_id, step.input, now=current)
        if step.capability_id == "filesystem.edit":
            content = {field.key: field.value for field in step.parameters}["content"]
            current += timedelta(seconds=1)
            service.save_file(
                started.session_id,
                path=result.editor.path,
                content=content,
                now=current,
            )
    report = service.get_progress(started.session_id, now=current).post_incident
    state = sessions.get(started.session_id, now=current)

    assert report.hints_used == 1
    assert report.hint_cost == definition.hints[0].cost
    assert report.score == state.score


def test_hard_report_uses_actual_partial_recovery_and_full_chain():
    definition = convert_draft_to_definition(
        build_hard_draft("H-01", seed=41), created_at=NOW
    )
    report, state = _complete(definition)

    assert len(report.root_cause_chain) == 2
    assert report.primary_fault and report.secondary_fault
    assert report.partial_recovery_explanation
    assert any(
        step.phase.value == "partial_recovery" for step in report.repair_timeline
    )
    assert any(len(record.resolved_fault_ids) == 1 for record in state.command_history)
    assert report.repair_sequence != definition.post_incident.repair_sequence
    assert set(report.repair_actions) <= {
        record.command for record in state.command_history if record.success
    }


def test_hard_partial_recovery_does_not_publish_final_report():
    definition = convert_draft_to_definition(
        build_hard_draft("H-01", seed=41), created_at=NOW
    )
    service, sessions, started = _service_for(definition)
    current = NOW
    for step in definition.solution:
        current += timedelta(seconds=2)
        service.execute_command(started.session_id, step.input, now=current)
        state = sessions.get(started.session_id, now=current)
        if any(
            len(record.resolved_fault_ids) == 1
            for record in state.command_history
        ):
            break

    view = service.get_progress(started.session_id, now=current)
    assert view.progress.mission_complete is False
    assert view.post_incident is None


def test_partial_recovery_is_hidden_when_history_did_not_record_it():
    definition = convert_draft_to_definition(
        build_hard_draft("H-01", seed=41), created_at=NOW
    )
    _, state = _complete(definition)
    state.command_history.clear()
    analysis = build_post_incident_analysis(definition, state)

    assert analysis.partial_recovery_seen is False
    assert all(
        step.phase.value != "partial_recovery" for step in analysis.repair_sequence
    )


def test_hard_reverse_repair_order_is_preserved_in_report():
    definition = convert_draft_to_definition(
        build_hard_draft("H-01", seed=37), created_at=NOW
    )
    service, _, started = _service_for(definition)
    commands = (
        "ssh app-0037",
        "restorecon -R /opt/orders-api",
        "systemctl restart orders-api",
        "ssh data-0037",
        "firewall-cmd --permanent --add-port=5432/tcp",
        "firewall-cmd --reload",
        "ssh client-0037",
        "curl http://portal.internal",
    )
    current = NOW
    for command in commands:
        current += timedelta(seconds=1)
        service.execute_command(started.session_id, command, now=current)
    report = service.get_progress(started.session_id, now=current).post_incident
    descriptions = [step.description for step in report.repair_timeline]

    assert report is not None
    assert descriptions[0].startswith("Przywrócono oczekiwany kontekst SELinux")
    assert next(index for index, text in enumerate(descriptions) if "firewalld" in text) > 0
    assert report.secondary_fault in report.partial_recovery_explanation
    assert report.repair_actions == tuple(
        command
        for command in commands
        if command.startswith(("restorecon", "systemctl restart", "firewall-cmd"))
    )


@pytest.mark.parametrize(
    ("difficulty", "definition"),
    (
        (
            DifficultyLevel.EASY,
            DeterministicIncidentGenerator().generate(
                DifficultyLevel.EASY, seed=5, now=NOW
            ),
        ),
        (
            DifficultyLevel.MEDIUM,
            convert_draft_to_definition(
                build_medium_draft("networkmanager-dns-invalid", seed=5),
                created_at=NOW,
            ),
        ),
        (
            DifficultyLevel.HARD,
            convert_draft_to_definition(
                build_hard_draft("H-02", seed=5), created_at=NOW
            ),
        ),
    ),
)
def test_active_public_dto_does_not_expose_report_or_relevance_metadata(
    difficulty, definition
):
    service, _, started = _service_for(definition)
    payload = service.get_progress(started.session_id, now=NOW).model_dump(
        mode="json", exclude_none=True
    )
    serialized = str(payload).casefold()

    assert difficulty is definition.difficulty
    assert "post_incident" not in payload
    for hidden in (
        "root_cause",
        "root_cause_chain",
        "command_review",
        "command_relevance",
        "capability_id",
        "fault_type",
        "provider",
        "model",
    ):
        assert hidden not in serialized


def test_completed_report_contains_public_data_only_and_is_deterministic():
    definition = convert_draft_to_definition(
        build_medium_draft("external-firewall-mismatch", seed=17),
        created_at=NOW,
    )
    report, state = _complete(definition)
    first = build_post_incident_analysis(definition, state)
    second = build_post_incident_analysis(definition, state.model_copy(deep=True))
    serialized = report.model_dump_json().casefold()

    assert first == second
    for hidden in (
        "capability_id",
        "fault_type",
        "resolution_condition",
        "raw_response",
        "provider",
        "generation_source",
        "diagnostic_milestones\":[\"",
    ):
        assert hidden not in serialized
