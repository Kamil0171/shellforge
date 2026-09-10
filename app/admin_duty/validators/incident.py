from datetime import timedelta
from ipaddress import ip_interface

from app.admin_duty.domain.definition import (
    ComponentType,
    GenerationSource,
    IncidentDefinition,
    ResourceType,
)
from app.admin_duty.domain.difficulty import get_difficulty_profile
from app.admin_duty.domain.objectives import evaluate_objectives
from app.admin_duty.domain.progress import get_session_progress
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.dynamic_command_parser import parse_dynamic_command
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.rocky.registry import HANDLERS


class IncidentValidationError(ValueError):
    pass


class IncidentReplayError(IncidentValidationError):
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


def _require_unique(values, *, name: str) -> None:
    values = tuple(values)
    if len(values) != len(set(values)):
        raise IncidentValidationError(f"Identyfikatory {name} nie są unikalne.")


def _validate_dependency_cycles(definition: IncidentDefinition) -> None:
    graph: dict[str, set[str]] = {}
    for dependency in definition.service_dependencies:
        graph.setdefault(dependency.source_service_id, set()).add(
            dependency.target_service_id
        )

    visited: set[str] = set()
    active: set[str] = set()

    def visit(service_id: str) -> None:
        if service_id in active:
            raise IncidentValidationError("Graf zależności usług zawiera cykl.")
        if service_id in visited:
            return
        active.add(service_id)
        for target_id in graph.get(service_id, set()):
            visit(target_id)
        active.remove(service_id)
        visited.add(service_id)

    for service_id in graph:
        visit(service_id)


def _validate_v3_references(definition: IncidentDefinition) -> None:
    resources = definition.initial_world_state.resources
    resource_by_id = {resource.resource_id: resource for resource in resources}
    services = {
        resource.resource_id: resource
        for resource in resources
        if resource.resource_type is ResourceType.SERVICE
    }
    hosts = {
        resource.resource_id: resource
        for resource in resources
        if resource.resource_type is ResourceType.HOST
    }

    _require_unique(
        (item.dependency_id for item in definition.service_dependencies),
        name="service dependencies",
    )
    _require_unique(
        (item.requirement_id for item in definition.package_requirements),
        name="package requirements",
    )
    _require_unique(
        (item.requirement_id for item in definition.configuration_requirements),
        name="configuration requirements",
    )
    _require_unique(
        (item.rule_id for item in definition.symptom_propagation),
        name="symptom propagation",
    )

    for resource in resources:
        if resource.parent_id is not None and resource.parent_id not in resource_by_id:
            raise IncidentValidationError("Zasób wskazuje nieznanego rodzica.")
        if any(dependency not in resource_by_id for dependency in resource.dependencies):
            raise IncidentValidationError("Zasób zawiera dangling dependency.")
        if resource.resource_type is ResourceType.SERVICE and resource.parent_id not in hosts:
            raise IncidentValidationError("Usługa musi należeć do znanego hosta.")

    bindings: set[tuple[str, int]] = set()
    for service in services.values():
        port = _field_map(service.attributes).get("port")
        if port is None:
            continue
        if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
            raise IncidentValidationError("Usługa zawiera nieprawidłowy port.")
        binding = (service.parent_id, port)
        if binding in bindings:
            raise IncidentValidationError("Host zawiera niemożliwe powiązanie portów.")
        bindings.add(binding)

    for dependency in definition.service_dependencies:
        source = services.get(dependency.source_service_id)
        target = services.get(dependency.target_service_id)
        if source is None or target is None:
            raise IncidentValidationError("Dependency wskazuje nieznaną usługę.")
        if dependency.source_service_id == dependency.target_service_id:
            raise IncidentValidationError("Usługa nie może zależeć od samej siebie.")
        if dependency.target_host_id not in hosts:
            raise IncidentValidationError("Dependency wskazuje nieznany host.")
        if dependency.source_host_id not in hosts:
            raise IncidentValidationError("Dependency wskazuje nieznany host źródłowy.")
        if source.parent_id != dependency.source_host_id:
            raise IncidentValidationError(
                "Dependency wskazuje niewłaściwy host usługi źródłowej."
            )
        if target.parent_id != dependency.target_host_id:
            raise IncidentValidationError("Dependency wskazuje niewłaściwy host usługi.")
        if _field_map(target.attributes).get("port") != dependency.port:
            raise IncidentValidationError("Port dependency nie odpowiada usłudze docelowej.")

    for requirement in definition.package_requirements:
        service = services.get(requirement.service_id)
        if service is None or requirement.host_id not in hosts:
            raise IncidentValidationError("Package requirement wskazuje nieznany zasób.")
        if service.parent_id != requirement.host_id:
            raise IncidentValidationError("Package requirement wskazuje niewłaściwy host.")

    for requirement in definition.configuration_requirements:
        service = services.get(requirement.service_id)
        resource = resource_by_id.get(requirement.file_resource_id)
        if service is None or requirement.host_id not in hosts or resource is None:
            raise IncidentValidationError(
                "Configuration requirement wskazuje nieznany zasób."
            )
        if resource.resource_type is not ResourceType.FILE:
            raise IncidentValidationError("Configuration requirement wymaga pliku.")
        if service.parent_id != requirement.host_id or resource.parent_id != requirement.host_id:
            raise IncidentValidationError(
                "Configuration requirement wskazuje niewłaściwy host."
            )

    dependency_ids = {
        dependency.dependency_id for dependency in definition.service_dependencies
    }
    for rule in definition.symptom_propagation:
        if rule.dependency_id not in dependency_ids:
            raise IncidentValidationError("Propagacja wskazuje nieznane dependency.")
        if rule.affected_resource_id not in resource_by_id:
            raise IncidentValidationError("Propagacja wskazuje nieznany zasób.")

    _validate_dependency_cycles(definition)

    addresses = []
    for host in hosts.values():
        address = _field_map(host.attributes).get("address")
        if not isinstance(address, str):
            continue
        try:
            addresses.append(str(ip_interface(address).ip))
        except ValueError as error:
            raise IncidentValidationError("Host zawiera nieprawidłowy adres IP.") from error
    if len(addresses) != len(set(addresses)):
        raise IncidentValidationError("Adresy hostów nie są unikalne.")

    if definition.schema_version == "3.0":
        if not definition.service_dependencies:
            raise IncidentValidationError("IncidentDefinition V3 wymaga grafu zależności.")
        if definition.post_incident is None:
            raise IncidentValidationError("IncidentDefinition V3 wymaga danych post-incident.")


def _validate_post_incident(definition: IncidentDefinition) -> None:
    if definition.post_incident is None:
        return
    services = {
        resource.resource_id
        for resource in definition.initial_world_state.resources
        if resource.resource_type is ResourceType.SERVICE
    }
    if any(
        service_id not in services
        for service_id in definition.post_incident.affected_service_ids
    ):
        raise IncidentValidationError("Post-incident wskazuje nieznaną usługę.")
    capabilities = set(definition.capabilities.command_capability_ids)
    if any(
        capability not in capabilities
        for capability in definition.post_incident.repair_capability_ids
    ):
        raise IncidentValidationError("Post-incident wskazuje nieznane capability.")


def _validate_ai_public_data(definition):
    from app.admin_duty.components import FAULT_TEMPLATES

    if definition.generation.generation_source is not GenerationSource.AI:
        return
    terms = {
        term.casefold()
        for fault in FAULT_TEMPLATES
        for term in fault.forbidden_public_terms
    } | {
        "python3-psycopg2", "restorecon", "httpd_sys_content_t", "5432/tcp",
        "add-service=https", "nmcli con mod", "firewall-cmd --add", "chmod ",
        "błędny kontekst", "brak pakietu", "blokuje port", "błędny dns",
    }
    if definition.post_incident:
        terms.add(definition.post_incident.root_cause.casefold())
    public_values = [
        definition.presentation.model_dump_json(),
        *(objective.label for objective in definition.objectives),
        *(objective.objective_id for objective in definition.objectives),
        *(item.interaction_id for item in definition.initial_world_state.map.interactions),
    ]
    for resource in definition.initial_world_state.resources:
        public_values.extend((resource.resource_id, resource.state))
        public_values.extend(
            str(field.value) for field in resource.attributes
            if field.key in {"hostname", "service_name", "role", "public_health"}
        )
    for value in public_values:
        if any(term in value.casefold() for term in terms if term):
            raise IncidentValidationError("Publiczne dane AI ujawniają przyczynę awarii.")
    for resource in definition.initial_world_state.resources:
        fields = _field_map(resource.attributes)
        for key in ("hostname", "service_name"):
            if key in fields:
                import re

                if not isinstance(fields[key], str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]{0,80}", fields[key]):
                    raise IncidentValidationError("Publiczna nazwa zasobu musi być nazwą techniczną.")


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
        _require_unique((item.fault_id for item in definition.faults), name="faultów")
        _require_unique(
            (item.symptom_id for item in definition.symptoms), name="symptomów"
        )
        _require_unique(
            (item.objective_id for item in definition.objectives), name="objectives"
        )
        if any(f.target_resource_id not in resource_id_set for f in definition.faults):
            raise IncidentValidationError("Fault wskazuje nieznany zasób.")
        if any(
            s.source_resource_id is not None
            and s.source_resource_id not in resource_id_set
            for s in definition.symptoms
        ):
            raise IncidentValidationError("Symptom wskazuje nieznany zasób.")
        if any(
            o.completion_condition is not None
            and o.completion_condition.resource_id not in resource_id_set
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
        if any(
            objective.completion_condition is None
            and not objective.completion_fact_ids
            for objective in definition.objectives
        ):
            raise IncidentValidationError(
                "Objective wymaga warunku stanu lub faktu diagnostycznego."
            )
        if (
            definition.generation.generation_source is GenerationSource.AI
            and not definition.generation.model
        ):
            raise IncidentValidationError("Scenariusz AI wymaga nazwy modelu.")

        _validate_v3_references(definition)
        _validate_post_incident(definition)
        _validate_ai_public_data(definition)

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
        if not capabilities <= set(HANDLERS):
            raise IncidentValidationError("Definicja zawiera nieznane capability.")
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
        for requirement in definition.package_requirements:
            if (
                requirement.package_name
                not in state.host_runtimes[
                    requirement.host_id
                ].packages.available_packages
            ):
                raise IncidentValidationError("Package requirement używa nieznanego pakietu.")
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
                    now=definition.created_at + timedelta(seconds=index * 2),
                )
                if step.capability_id == "filesystem.edit":
                    content = _field_map(step.parameters).get("content")
                    if not isinstance(content, str) or result.editor is None:
                        raise IncidentValidationError(
                            "Reference solution edycji wymaga treści pliku."
                        )
                    result = service.save_file(
                        definition,
                        state,
                        path=result.editor.path,
                        content=content,
                        now=definition.created_at + timedelta(seconds=index * 2 + 1),
                    )
                if result.success is not step.expected_success:
                    raise IncidentValidationError(
                        "Krok reference solution zwrócił inny status niż oczekiwany."
                    )
                final_progress = result.progress
        except IncidentValidationError as error:
            raise IncidentReplayError("Replay reference solution nie przeszedł walidacji.") from error
        except Exception as error:
            raise IncidentReplayError(
                "Replay reference solution zakończył się błędem."
            ) from error

        if not final_progress.mission_complete:
            raise IncidentReplayError(
                "Reference solution nie kończy wymaganych objectives."
            )
        if definition.model_dump_json() != before:
            raise IncidentValidationError("Validator zmodyfikował IncidentDefinition.")
        return definition
