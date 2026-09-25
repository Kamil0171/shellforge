import asyncio
import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine, select

import app.admin_duty.repositories.sql as sql_repository_module
import app.seed as seed_module
from app.admin_duty.domain.definition import GenerationSource, IncidentRecoveryState
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.persistence import SessionSnapshotError
from app.admin_duty.domain.recovery import get_incident_recovery_state
from app.admin_duty.domain.runtime import SessionStatus, touch_session
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    SESSION_TTL,
    RepositoryUnavailableError,
    SessionConflictError,
    SessionNotFoundError,
    SQLIncidentSessionRepository,
)
from app.admin_duty.services import DynamicIncidentService
from app.models import DynamicIncidentSession

NOW = datetime(2026, 9, 25, 10, 0, tzinfo=UTC)


def build_engine(database_path):
    engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    return engine


def build_service(engine, *, generator=None, generation_service=None):
    repository = SQLIncidentSessionRepository(engine)
    service = DynamicIncidentService(
        generator=generator or DeterministicIncidentGenerator(),
        generation_service=generation_service,
        aggregate_repository=repository,
    )
    return service, repository


def get_record(engine, session_id):
    with Session(engine) as session:
        return session.get(DynamicIncidentSession, str(session_id))


def execute_solution_step(service, definition, session_id, step, current_time):
    result = service.execute_command(
        session_id,
        step.input,
        now=current_time,
    )
    if step.capability_id == "filesystem.edit":
        content = {field.key: field.value for field in step.parameters}["content"]
        current_time += timedelta(seconds=1)
        result = service.save_file(
            session_id,
            path=result.editor.path,
            content=content,
            now=current_time,
        )
    assert result.success is step.expected_success
    return current_time


def test_create_and_new_repository_instance_restore_same_aggregate(tmp_path):
    database_path = tmp_path / "sessions.db"
    engine_a = build_engine(database_path)
    service_a, repository_a = build_service(engine_a)
    started = service_a.start_session(DifficultyLevel.EASY, seed=11, now=NOW)
    before = repository_a.get(started.session_id, now=NOW)

    engine_a.dispose()
    engine_b = build_engine(database_path)
    _, repository_b = build_service(engine_b)
    restored = repository_b.get(started.session_id, now=NOW)

    assert restored.definition == before.definition
    assert restored.state == before.state
    assert restored.state is not before.state
    assert restored.state.host_runtimes is not before.state.host_runtimes
    record = get_record(engine_b, started.session_id)
    assert record.schema_version == 1
    assert record.snapshot_json.startswith('{"schema_version":1,')
    assert record.expires_at == NOW.replace(tzinfo=None) + SESSION_TTL


def test_hard_partial_recovery_restart_completion_and_report(tmp_path):
    database_path = tmp_path / "hard-restart.db"
    engine_a = build_engine(database_path)
    service_a, repository_a = build_service(engine_a)
    started = service_a.start_session(DifficultyLevel.HARD, seed=1, now=NOW)
    definition = repository_a.get(started.session_id, now=NOW).definition
    current_time = NOW
    remaining_steps = []

    for index, step in enumerate(definition.solution):
        current_time += timedelta(seconds=2)
        current_time = execute_solution_step(
            service_a,
            definition,
            started.session_id,
            step,
            current_time,
        )
        aggregate = repository_a.get(started.session_id, now=current_time)
        if (
            get_incident_recovery_state(aggregate.definition, aggregate.state)
            is IncidentRecoveryState.PARTIALLY_RECOVERED
        ):
            remaining_steps = list(definition.solution[index + 1 :])
            break
    else:
        pytest.fail("Scenariusz HARD nie osiągnął partial recovery.")

    before_restart = repository_a.get(started.session_id, now=current_time)
    assert before_restart.state.status is SessionStatus.ACTIVE
    assert before_restart.state.command_history
    assert before_restart.state.discovered_fact_ids

    engine_a.dispose()
    engine_b = build_engine(database_path)
    service_b, repository_b = build_service(engine_b)
    after_restart = repository_b.get(started.session_id, now=current_time)

    assert after_restart.definition == before_restart.definition
    assert after_restart.state == before_restart.state
    assert (
        get_incident_recovery_state(after_restart.definition, after_restart.state)
        is IncidentRecoveryState.PARTIALLY_RECOVERED
    )

    for step in remaining_steps:
        current_time += timedelta(seconds=2)
        current_time = execute_solution_step(
            service_b,
            definition,
            started.session_id,
            step,
            current_time,
        )

    completed = service_b.get_progress(started.session_id, now=current_time)
    assert completed.progress.mission_complete
    assert completed.progress.status is SessionStatus.COMPLETED
    assert completed.post_incident is not None
    completed_record = get_record(engine_b, started.session_id)
    assert completed_record.completed_at is not None
    completed_at = completed_record.completed_at

    engine_b.dispose()
    engine_c = build_engine(database_path)
    service_c, repository_c = build_service(engine_c)
    restored_completed = repository_c.get(started.session_id, now=current_time)
    report = service_c.get_progress(started.session_id, now=current_time)

    assert restored_completed.state.status is SessionStatus.COMPLETED
    assert report.progress.mission_complete
    assert report.post_incident == completed.post_incident
    assert report.post_incident.commands_used == tuple(
        record.command for record in restored_completed.state.command_history
    )

    current_time += timedelta(seconds=1)
    service_c.end_session(started.session_id, now=current_time)
    assert get_record(engine_c, started.session_id).completed_at == completed_at


def test_complete_virtual_rocky_state_survives_restart(tmp_path):
    database_path = tmp_path / "rocky-state.db"
    engine_a = build_engine(database_path)
    _, repository_a = build_service(engine_a)
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.HARD,
        seed=2,
        now=NOW,
    )
    from app.admin_duty.domain.runtime import create_session_runtime

    state = create_session_runtime(definition, now=NOW)
    repository_a.create(definition, state, now=NOW)
    aggregate = repository_a.get(state.session_id, now=NOW)
    mutated = aggregate.state
    expected_revision = mutated.revision
    touch_session(mutated, now=NOW + timedelta(minutes=1))
    host_ids = list(mutated.host_runtimes)
    mutated.active_host_id = host_ids[-1]
    mutated.current_working_directory = "/tmp"
    mutated.host_working_directories[host_ids[-1]] = "/tmp"
    rocky = mutated.virtual_rocky
    file_entry = rocky.filesystem["/etc/os-release"]
    file_entry.content = "persisted\n"
    file_entry.mode = "0600"
    file_entry.owner = "operator"
    file_entry.group = "operator"
    rocky.systemd_unit_cache["persisted.service"] = "[Service]\nExecStart=/bin/true\n"
    rocky.systemd_enabled_units.add("persisted.service")
    rocky.daemon_reload_required = True
    rocky.journal_entries.append("persisted journal entry")
    rocky.packages.cache_clean = True
    rocky.packages.enabled_repositories.discard("extras")
    rocky.firewall.runtime_ports.add("8443/tcp")
    rocky.firewall.permanent_services.add("https")
    rocky.selinux.mode = "Permissive"
    rocky.selinux.file_contexts["/tmp"] = "system_u:object_r:tmp_t:s0"
    connection = next(iter(rocky.network.connections))
    rocky.network.connections[connection] = False
    rocky.network.connection_dns_servers[connection] = ("1.1.1.1",)
    rocky.network.routes.append("203.0.113.0/24 via 10.24.8.1")
    interface = next(iter(rocky.network.interfaces.values()))
    interface.state = "down"
    mutated.discovered_fact_ids.add("persistence:verified")
    mutated.score -= 7
    repository_a.update(
        definition,
        mutated,
        expected_revision=expected_revision,
        now=mutated.last_activity,
    )

    engine_a.dispose()
    engine_b = build_engine(database_path)
    _, repository_b = build_service(engine_b)
    restored = repository_b.get(state.session_id, now=mutated.last_activity)

    assert restored.state == mutated
    assert restored.state.virtual_rocky.filesystem["/etc/os-release"].content == (
        "persisted\n"
    )
    assert restored.state.virtual_rocky.daemon_reload_required
    assert restored.state.virtual_rocky.firewall.runtime_ports == {"8443/tcp"}
    assert restored.state.virtual_rocky.selinux.mode == "Permissive"


def test_optimistic_lock_rejects_second_writer(tmp_path):
    engine = build_engine(tmp_path / "locking.db")
    service, repository = build_service(engine)
    started = service.start_session(DifficultyLevel.EASY, seed=3, now=NOW)
    first = repository.get(started.session_id, now=NOW)
    stale = repository.get(started.session_id, now=NOW)
    mutation_time = NOW + timedelta(minutes=1)
    touch_session(first.state, now=mutation_time)
    touch_session(stale.state, now=mutation_time)

    repository.update(
        first.definition,
        first.state,
        expected_revision=0,
        now=mutation_time,
    )
    with pytest.raises(SessionConflictError):
        repository.update(
            stale.definition,
            stale.state,
            expected_revision=0,
            now=mutation_time,
        )

    assert repository.get(started.session_id, now=mutation_time).state == first.state


def test_session_isolation_survives_restart(tmp_path):
    database_path = tmp_path / "isolation.db"
    engine_a = build_engine(database_path)
    service_a, repository_a = build_service(engine_a)
    first = service_a.start_session(DifficultyLevel.EASY, seed=4, now=NOW)
    second = service_a.start_session(DifficultyLevel.EASY, seed=4, now=NOW)
    first_before = repository_a.get(first.session_id, now=NOW)
    second_before = repository_a.get(second.session_id, now=NOW)
    service_a.execute_command(
        first.session_id,
        "pwd",
        now=NOW + timedelta(minutes=1),
    )

    engine_a.dispose()
    engine_b = build_engine(database_path)
    _, repository_b = build_service(engine_b)
    first_after = repository_b.get(first.session_id, now=NOW + timedelta(minutes=1))
    second_after = repository_b.get(second.session_id, now=NOW + timedelta(minutes=1))

    assert first_after.state.commands_used == first_before.state.commands_used + 1
    assert second_after.state == second_before.state
    first_after.state.virtual_rocky.filesystem["/etc/os-release"].content = "changed"
    assert (
        repository_b.get(second.session_id, now=NOW + timedelta(minutes=1))
        .state.virtual_rocky.filesystem["/etc/os-release"]
        .content
        != "changed"
    )


def test_ttl_is_persisted_get_does_not_extend_and_mutation_does(tmp_path):
    engine = build_engine(tmp_path / "ttl.db")
    service, repository = build_service(engine)
    started = service.start_session(DifficultyLevel.EASY, seed=5, now=NOW)
    initial_expiry = get_record(engine, started.session_id).expires_at

    service.get_progress(started.session_id, now=NOW + timedelta(minutes=10))
    assert get_record(engine, started.session_id).expires_at == initial_expiry

    mutation_time = NOW + timedelta(minutes=20)
    service.request_hint(started.session_id, now=mutation_time)
    updated_expiry = get_record(engine, started.session_id).expires_at
    assert updated_expiry == mutation_time.replace(tzinfo=None) + SESSION_TTL

    with pytest.raises(SessionNotFoundError):
        repository.get(
            started.session_id,
            now=mutation_time + SESSION_TTL,
        )
    assert get_record(engine, started.session_id) is None


def test_cleanup_removes_all_expired_records(tmp_path):
    engine = build_engine(tmp_path / "cleanup.db")
    service, repository = build_service(engine)
    first = service.start_session(DifficultyLevel.EASY, seed=6, now=NOW)
    second = service.start_session(DifficultyLevel.EASY, seed=7, now=NOW)

    expired = repository.cleanup_expired(now=NOW + SESSION_TTL)

    assert set(expired) == {first.session_id, second.session_id}
    assert get_record(engine, first.session_id) is None
    assert get_record(engine, second.session_id) is None


@pytest.mark.parametrize(
    "corruption",
    [
        "invalid-json",
        "missing-version",
        "unknown-version",
        "invalid-typed-payload",
        "session-id-mismatch",
        "scenario-id-mismatch",
        "revision-mismatch",
        "status-mismatch",
        "active-host-mismatch",
        "objective-id-mismatch",
    ],
)
def test_corrupt_or_incompatible_snapshot_fails_safe(tmp_path, corruption):
    engine = build_engine(tmp_path / f"corrupt-{corruption}.db")
    service, repository = build_service(engine)
    started = service.start_session(DifficultyLevel.EASY, seed=8, now=NOW)

    with Session(engine) as session:
        record = session.get(DynamicIncidentSession, str(started.session_id))
        if corruption == "invalid-json":
            record.snapshot_json = "{"
        else:
            payload = json.loads(record.snapshot_json)
            if corruption == "missing-version":
                payload.pop("schema_version")
            elif corruption == "unknown-version":
                payload["schema_version"] = 999
                record.schema_version = 999
            elif corruption == "invalid-typed-payload":
                payload["runtime_state"]["score"] = -1
            elif corruption == "session-id-mismatch":
                payload["runtime_state"]["session_id"] = str(uuid4())
            elif corruption == "scenario-id-mismatch":
                scenario_id = str(uuid4())
                payload["incident_definition"]["scenario_id"] = scenario_id
                payload["runtime_state"]["scenario_id"] = scenario_id
            elif corruption == "revision-mismatch":
                record.revision += 1
            elif corruption == "status-mismatch":
                record.status = "completed"
            elif corruption == "active-host-mismatch":
                payload["runtime_state"]["active_host_id"] = "missing-host"
            elif corruption == "objective-id-mismatch":
                payload["runtime_state"]["completed_objective_ids"] = [
                    "missing-objective"
                ]
            record.snapshot_json = json.dumps(payload)
        session.add(record)
        session.commit()

    with pytest.raises(SessionSnapshotError):
        repository.get(started.session_id, now=NOW)


def test_commit_failure_preserves_previous_snapshot(tmp_path, monkeypatch):
    engine = build_engine(tmp_path / "commit-failure.db")
    service, repository = build_service(engine)
    started = service.start_session(DifficultyLevel.EASY, seed=9, now=NOW)
    before = repository.get(started.session_id, now=NOW)

    def fail_commit(self):
        raise SQLAlchemyError("commit failed")

    monkeypatch.setattr(sql_repository_module.Session, "commit", fail_commit)
    with pytest.raises(RepositoryUnavailableError):
        service.execute_command(
            started.session_id,
            "pwd",
            now=NOW + timedelta(minutes=1),
        )

    monkeypatch.undo()
    restored = repository.get(started.session_id, now=NOW + timedelta(minutes=1))
    assert restored.state == before.state


def test_ai_session_restore_never_calls_generation_again(tmp_path):
    database_path = tmp_path / "ai-restart.db"
    generated = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY,
        seed=10,
        now=NOW,
    )
    generated = generated.model_copy(
        update={
            "generation": generated.generation.model_copy(
                update={
                    "generation_source": GenerationSource.AI,
                    "model": "fake-model",
                }
            )
        }
    )

    class InitialGenerationService:
        calls = 0

        async def generate(self, request, *, now=None):
            self.calls += 1
            return generated

    class FailIfCalled:
        def generate(self, *args, **kwargs):
            raise AssertionError("Generator nie może być wywołany podczas restore.")

    class FailGenerationService:
        async def generate(self, *args, **kwargs):
            raise AssertionError("AI nie może być wywołane podczas restore.")

    initial_generation = InitialGenerationService()
    engine_a = build_engine(database_path)
    service_a, _ = build_service(
        engine_a,
        generation_service=initial_generation,
    )
    started = asyncio.run(
        service_a.start_session_async(DifficultyLevel.EASY, seed=10, now=NOW)
    )
    assert initial_generation.calls == 1
    engine_a.dispose()

    engine_b = build_engine(database_path)
    service_b, repository_b = build_service(
        engine_b,
        generator=FailIfCalled(),
        generation_service=FailGenerationService(),
    )
    restored = service_b.get_progress(started.session_id, now=NOW)
    aggregate = repository_b.get(started.session_id, now=NOW)

    assert restored.progress.session_id == started.session_id
    assert aggregate.definition.generation.generation_source is GenerationSource.AI
    assert aggregate.definition.generation.model == "fake-model"


def test_application_reseed_does_not_remove_persisted_session(tmp_path, monkeypatch):
    engine = build_engine(tmp_path / "reseed.db")
    service, repository = build_service(engine)
    started = service.start_session(DifficultyLevel.EASY, seed=12, now=NOW)
    before = repository.get(started.session_id, now=NOW)
    monkeypatch.setattr(seed_module, "engine", engine)

    seed_module.seed_database()
    seed_module.seed_database()

    after = repository.get(started.session_id, now=NOW)
    assert after == before
    with Session(engine) as session:
        assert session.exec(select(DynamicIncidentSession)).one().session_id == str(
            started.session_id
        )
