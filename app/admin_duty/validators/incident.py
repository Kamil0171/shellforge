from datetime import timedelta

from app.admin_duty.domain.definition import (
    ComponentType,
    IncidentDefinition,
    ResourceType,
)
from app.admin_duty.domain.difficulty import get_difficulty_profile
from app.admin_duty.domain.objectives import evaluate_objectives
from app.admin_duty.domain.progress import get_session_progress
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.dynamic_command_parser import parse_dynamic_command
from app.admin_duty.dynamic_command_service import DynamicCommandService


class IncidentValidationError(ValueError):
    pass


def _require_deterministic_order(items, *, name: str, key) -> None:
    if tuple(items) != tuple(sorted(items, key=key)):
        raise IncidentValidationError(f"Kolejność {name} nie jest deterministyczna.")

    orders = [item.order for item in items]
    if len(orders) != len(set(orders)):
        raise IncidentValidationError(f"Kolejność {name} zawiera duplikaty.")
    if orders != list(range(1, len(items) + 1)):
        raise IncidentValidationError(f"Kolejność {name} nie jest ciągła od 1.")


def _field_map(fields) -> dict:
    return {field.key: field.value for field in fields}


class IncidentValidator:
    def validate(self, definition: IncidentDefinition) -> IncidentDefinition:
        before = definition.model_dump_json()
        profile = get_difficulty_profile(definition.difficulty)
        resources = definition.initial_world_state.resources
        resource_ids = [resource.resource_id for resource in resources]
        resource_id_set = set(resource_ids)
        hosts = [r for r in resources if r.resource_type is ResourceType.HOST]

        if not profile.min_hosts <= len(hosts) <= profile.max_hosts:
            raise IncidentValidationError("Liczba hostów jest niezgodna z profilem.")
        if not profile.min_faults <= len(definition.faults) <= profile.max_faults:
            raise IncidentValidationError("Liczba faultów jest niezgodna z profilem.")
        if len(resource_ids) != len(resource_id_set):
            raise IncidentValidationError("Identyfikatory zasobów nie są unikalne.")
        if any(f.target_resource_id not in resource_id_set for f in definition.faults):
            raise IncidentValidationError("Fault wskazuje nieznany zasób.")
        if any(
            s.source_resource_id is not None
            and s.source_resource_id not in resource_id_set
            for s in definition.symptoms
        ):
            raise IncidentValidationError("Symptom wskazuje nieznany zasób.")
        if any(
            o.completion_condition.resource_id not in resource_id_set
            for o in definition.objectives
        ):
            raise IncidentValidationError("Objective wskazuje nieznany zasób.")
        if any(
            i.target_resource_id is not None
            and i.target_resource_id not in resource_id_set
            for i in definition.initial_world_state.map.interactions
        ):
            raise IncidentValidationError("Interakcja mapy wskazuje nieznany zasób.")
        if not any(objective.required for objective in definition.objectives):
            raise IncidentValidationError("Incydent wymaga przynajmniej jednego celu.")
        if len(definition.hints) > profile.hint_limit:
            raise IncidentValidationError("Liczba podpowiedzi przekracza profil.")

        _require_deterministic_order(
            definition.objectives,
            name="objectives",
            key=lambda item: (item.order, item.objective_id),
        )
        _require_deterministic_order(
            definition.hints, name="hints", key=lambda item: item.order
        )
        _require_deterministic_order(
            definition.solution, name="solution", key=lambda item: item.order
        )

        capabilities = set(definition.capabilities.command_capability_ids)
        for step in definition.solution:
            if step.capability_id not in capabilities:
                raise IncidentValidationError(
                    "Reference solution używa niedostępnego capability."
                )
            try:
                request = parse_dynamic_command(step.input)
            except ValueError as error:
                raise IncidentValidationError(
                    "Reference solution zawiera nieprawidłową komendę."
                ) from error
            if request.command_id != step.capability_id:
                raise IncidentValidationError(
                    "Komenda solution nie odpowiada deklarowanemu capability."
                )

        component_types = {r.component_type for r in definition.generation.components}
        required_types = {
            ComponentType.ENVIRONMENT,
            ComponentType.MAP,
            ComponentType.FAULT,
            ComponentType.SYMPTOM,
            ComponentType.OBJECTIVE,
            ComponentType.CAPABILITY,
            ComponentType.SCORING_POLICY,
        }
        if not required_types <= component_types:
            raise IncidentValidationError("Provenance komponentów jest niepełne.")

        references = [
            (r.component_type, r.component_id, r.version)
            for r in definition.generation.components
        ]
        if len(references) != len(set(references)):
            raise IncidentValidationError("Provenance zawiera duplikaty.")

        fault_components = {
            (_field_map(fault.parameters).get("component_id"), fault.version)
            for fault in definition.faults
        }
        referenced_faults = {
            (r.component_id, r.version)
            for r in definition.generation.components
            if r.component_type is ComponentType.FAULT
        }
        if fault_components != referenced_faults:
            raise IncidentValidationError("Provenance faultów jest niespójne.")

        public_text = " ".join(
            (
                definition.presentation.title,
                definition.presentation.briefing,
                definition.presentation.main_objective,
            )
        ).casefold()
        for fault in definition.faults:
            terms = _field_map(fault.parameters).get("forbidden_public_terms", ())
            if not isinstance(terms, tuple):
                raise IncidentValidationError(
                    "Fault nie zawiera kontrolowanej listy terminów."
                )
            if any(
                term.casefold() in public_text
                for term in terms
                if isinstance(term, str)
            ):
                raise IncidentValidationError(
                    "Publiczna prezentacja ujawnia root cause incydentu."
                )

        state = create_session_runtime(definition, now=definition.created_at)
        initially_completed = evaluate_objectives(definition, state)
        required_ids = {
            objective.objective_id
            for objective in definition.objectives
            if objective.required
        }
        if initially_completed & required_ids:
            raise IncidentValidationError(
                "Wymagany objective jest ukończony w initial state."
            )
        if get_session_progress(definition, state).mission_complete:
            raise IncidentValidationError("Misja jest ukończona w initial state.")

        service = DynamicCommandService()
        final_progress = get_session_progress(definition, state)
        try:
            for index, step in enumerate(definition.solution, start=1):
                result = service.execute(
                    definition,
                    state,
                    step.input,
                    now=definition.created_at + timedelta(seconds=index),
                )
                if not result.success:
                    raise IncidentValidationError(
                        "Krok reference solution zakończył się niepowodzeniem."
                    )
                final_progress = result.progress
        except IncidentValidationError:
            raise
        except Exception as error:
            raise IncidentValidationError(
                "Replay reference solution zakończył się błędem."
            ) from error

        if not final_progress.mission_complete:
            raise IncidentValidationError(
                "Reference solution nie kończy wymaganych objectives."
            )
        if definition.model_dump_json() != before:
            raise IncidentValidationError("Validator zmodyfikował IncidentDefinition.")
        return definition
