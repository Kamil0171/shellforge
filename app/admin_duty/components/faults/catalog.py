from types import MappingProxyType
from typing import Final

from app.admin_duty.components.models import (
    AttributeMutationTemplate,
    ComponentMetadata,
    FaultTemplate,
    ObjectiveTemplate,
    ResourceRole,
    SolutionStepTemplate,
    StateMutationTemplate,
    SymptomTemplate,
)
from app.admin_duty.domain.definition import (
    CompletionCondition,
    ConditionOperator,
    DataField,
    FaultSeverity,
    Hint,
    ResourceType,
    SymptomVisibility,
)
from app.admin_duty.domain.difficulty import DifficultyLevel

COMPONENT_VERSION = "1.0"
SERVICE_OBJECTIVE = CompletionCondition(
    resource_id="template-service",
    field="current_state",
    operator=ConditionOperator.EQUALS,
    expected="running",
)


def _objective(component_id: str, label: str) -> ObjectiveTemplate:
    return ObjectiveTemplate(
        component_id=component_id,
        version=COMPONENT_VERSION,
        objective_id_template="restore-{primary_service}",
        label_template=label,
        resource_role=ResourceRole.PRIMARY_SERVICE,
        condition=SERVICE_OBJECTIVE,
        order=1,
    )


def _symptom(
    component_id: str,
    symptom_id: str,
    symptom_type: str,
    **data,
) -> SymptomTemplate:
    return SymptomTemplate(
        component_id=component_id,
        version=COMPONENT_VERSION,
        symptom_id=symptom_id,
        symptom_type=symptom_type,
        source_role=ResourceRole.PRIMARY_SERVICE,
        visibility=SymptomVisibility.BRIEFING,
        data=tuple(DataField(key=key, value=value) for key, value in data.items()),
    )


FAULT_TEMPLATES = (
    FaultTemplate(
        component_id="systemd-service-failed",
        version=COMPONENT_VERSION,
        metadata=ComponentMetadata(
            label="Zatrzymana usługa systemd",
            description="Usługa wymaga diagnozy stanu i ponownego uruchomienia.",
        ),
        fault_type="systemd_service_failed",
        compatible_difficulties=(DifficultyLevel.EASY,),
        target_role=ResourceRole.PRIMARY_SERVICE,
        required_resource_types=(ResourceType.SERVICE,),
        severity=FaultSeverity.LOW,
        state_mutations=(
            StateMutationTemplate(
                resource_role=ResourceRole.PRIMARY_SERVICE,
                new_state="failed",
            ),
        ),
        required_capabilities=("systemd.status", "systemd.restart"),
        symptom=_symptom(
            "symptom-service-unavailable",
            "service-unavailable",
            "service_unavailable",
            status_code=503,
        ),
        objective=_objective(
            "objective-restore-service",
            "Przywróć działanie usługi {primary_service}",
        ),
        hints=(
            Hint(order=1, text="Sprawdź bieżący stan wskazanej usługi.", cost=20),
            Hint(order=2, text="Usługa jest zarządzana przez systemd.", cost=30),
            Hint(order=3, text="Spróbuj ponownie uruchomić usługę.", cost=40),
        ),
        solution=(
            SolutionStepTemplate(
                order=1,
                capability_id="systemd.status",
                input_template="systemctl status {primary_service}",
                purpose="Sprawdź bieżący stan usługi.",
            ),
            SolutionStepTemplate(
                order=2,
                capability_id="systemd.restart",
                input_template="systemctl restart {primary_service}",
                purpose="Uruchom usługę ponownie.",
            ),
        ),
        briefing_addition="Problem pojawił się nagle, bez wcześniejszych zmian konfiguracji.",
        forbidden_public_terms=("stopped service", "ręcznie zatrzymana"),
    ),
    FaultTemplate(
        component_id="systemd-wrong-exec-start",
        version=COMPONENT_VERSION,
        metadata=ComponentMetadata(
            label="Nieprawidłowy cel ExecStart",
            description="Kontrolowana rozbieżność celu startowego usługi.",
        ),
        fault_type="systemd_wrong_exec_start",
        compatible_difficulties=(DifficultyLevel.EASY,),
        target_role=ResourceRole.PRIMARY_SERVICE,
        required_resource_types=(ResourceType.SERVICE,),
        required_context_keys=("expected_exec_target", "broken_exec_target"),
        severity=FaultSeverity.LOW,
        state_mutations=(
            StateMutationTemplate(
                resource_role=ResourceRole.PRIMARY_SERVICE,
                new_state="failed",
            ),
        ),
        attribute_mutations=(
            AttributeMutationTemplate(
                resource_role=ResourceRole.PRIMARY_SERVICE,
                attribute="configured_exec_start",
                value_context_key="broken_exec_target",
            ),
        ),
        required_capabilities=(
            "systemd.status",
            "systemd.cat",
            "filesystem.edit",
            "systemd.restart",
        ),
        symptom=_symptom(
            "symptom-service-start-failure",
            "service-start-failure",
            "service_start_failure",
            phase="startup",
        ),
        objective=_objective(
            "objective-restore-service-after-deployment",
            "Przywróć działanie usługi {primary_service}",
        ),
        hints=(
            Hint(order=1, text="Sprawdź stan usługi po ostatnim wdrożeniu.", cost=20),
            Hint(order=2, text="Porównaj aktywny cel startowy z oczekiwanym.", cost=30),
            Hint(
                order=3,
                text="Popraw ExecStart w pliku jednostki, wykonaj daemon-reload i restart.",
                cost=40,
            ),
        ),
        solution=(
            SolutionStepTemplate(
                order=1,
                capability_id="systemd.status",
                input_template="systemctl status {primary_service}",
                purpose="Sprawdź stan usługi.",
            ),
            SolutionStepTemplate(
                order=2,
                capability_id="systemd.cat",
                input_template="systemctl cat {primary_service}",
                purpose="Sprawdź kontrolowaną konfigurację startową.",
            ),
            SolutionStepTemplate(
                order=3,
                capability_id="filesystem.edit",
                content_template="{healthy_unit}",
                input_template=("nano {unit_path}"),
                purpose="Przywróć dozwolony cel startowy.",
            ),
            SolutionStepTemplate(
                order=4,
                capability_id="systemd.restart",
                input_template="systemctl restart {primary_service}",
                purpose="Uruchom usługę po korekcie.",
            ),
        ),
        briefing_addition="Problem rozpoczął się po ostatnim wdrożeniu aplikacji.",
        forbidden_public_terms=("execstart", "wrong exec", "cel startowy"),
    ),
    FaultTemplate(
        component_id="systemd-missing-environment-variable",
        version=COMPONENT_VERSION,
        metadata=ComponentMetadata(
            label="Brak wymaganej zmiennej środowiskowej",
            description="Usługa nie otrzymała kontrolowanej wartości środowiska.",
        ),
        fault_type="systemd_missing_environment_variable",
        compatible_difficulties=(DifficultyLevel.EASY,),
        target_role=ResourceRole.PRIMARY_SERVICE,
        required_resource_types=(ResourceType.SERVICE,),
        required_context_keys=("environment_variable", "environment_value"),
        severity=FaultSeverity.LOW,
        state_mutations=(
            StateMutationTemplate(
                resource_role=ResourceRole.PRIMARY_SERVICE,
                new_state="failed",
            ),
        ),
        attribute_mutations=(
            AttributeMutationTemplate(
                resource_role=ResourceRole.PRIMARY_SERVICE,
                attribute_context_key="environment_variable",
                attribute_prefix="environment.",
                remove=True,
            ),
        ),
        required_capabilities=(
            "systemd.status",
            "systemd.cat",
            "filesystem.edit",
            "systemd.restart",
        ),
        symptom=_symptom(
            "symptom-service-configuration-failure",
            "service-configuration-failure",
            "configuration_failure",
            phase="initialization",
        ),
        objective=_objective(
            "objective-restore-service-environment",
            "Przywróć działanie usługi {primary_service}",
        ),
        hints=(
            Hint(order=1, text="Sprawdź stan usługi i etap jej uruchamiania.", cost=20),
            Hint(order=2, text="Sprawdź wymagane środowisko procesu.", cost=30),
            Hint(
                order=3,
                text="Uzupełnij Environment w pliku jednostki, wykonaj daemon-reload i restart.",
                cost=40,
            ),
        ),
        solution=(
            SolutionStepTemplate(
                order=1,
                capability_id="systemd.status",
                input_template="systemctl status {primary_service}",
                purpose="Sprawdź stan usługi.",
            ),
            SolutionStepTemplate(
                order=2,
                capability_id="systemd.cat",
                input_template="systemctl cat {service_name}",
                purpose="Sprawdź wymagane środowisko usługi.",
            ),
            SolutionStepTemplate(
                order=3,
                capability_id="filesystem.edit",
                content_template="{healthy_unit}",
                input_template=("nano {unit_path}"),
                purpose="Przywróć kontrolowaną wartość środowiska.",
            ),
            SolutionStepTemplate(
                order=4,
                capability_id="systemd.restart",
                input_template="systemctl restart {primary_service}",
                purpose="Uruchom usługę po korekcie środowiska.",
            ),
        ),
        briefing_addition="Problem wystąpił po zmianie konfiguracji uruchomieniowej.",
        forbidden_public_terms=(
            "database_url",
            "queue_url",
            "upstream_url",
            "missing environment variable",
            "brakująca zmienna",
        ),
    ),
    FaultTemplate(
        component_id="systemd-permission-denied",
        version=COMPONENT_VERSION,
        metadata=ComponentMetadata(
            label="Nieprawidłowe uprawnienia pliku wykonywalnego",
            description="Kontrolowany tryb pliku blokuje start procesu usługi.",
        ),
        fault_type="systemd_permission_denied",
        compatible_difficulties=(DifficultyLevel.EASY,),
        target_role=ResourceRole.EXECUTABLE_FILE,
        required_resource_types=(ResourceType.FILE,),
        required_context_keys=("expected_file_mode", "broken_file_mode"),
        severity=FaultSeverity.LOW,
        state_mutations=(
            StateMutationTemplate(
                resource_role=ResourceRole.PRIMARY_SERVICE,
                new_state="failed",
            ),
        ),
        attribute_mutations=(
            AttributeMutationTemplate(
                resource_role=ResourceRole.EXECUTABLE_FILE,
                attribute="current_mode",
                value_context_key="broken_file_mode",
            ),
        ),
        required_capabilities=(
            "systemd.status",
            "filesystem.path-stat",
            "filesystem.chmod",
            "systemd.restart",
        ),
        symptom=_symptom(
            "symptom-service-execution-failure",
            "service-execution-failure",
            "execution_failure",
            phase="process_start",
        ),
        objective=_objective(
            "objective-restore-service-permissions",
            "Przywróć działanie usługi {primary_service}",
        ),
        hints=(
            Hint(
                order=1,
                text="Sprawdź stan usługi i sposób zakończenia procesu.",
                cost=20,
            ),
            Hint(
                order=2,
                text="Sprawdź stan kontrolowanego pliku wykonywalnego.",
                cost=30,
            ),
            Hint(
                order=3,
                text="Przywróć oczekiwany tryb pliku i wykonaj restart.",
                cost=40,
            ),
        ),
        solution=(
            SolutionStepTemplate(
                order=1,
                capability_id="systemd.status",
                input_template="systemctl status {primary_service}",
                purpose="Sprawdź stan usługi.",
            ),
            SolutionStepTemplate(
                order=2,
                capability_id="filesystem.path-stat",
                input_template="stat {executable_path}",
                purpose="Sprawdź kontrolowany stan pliku wykonywalnego.",
            ),
            SolutionStepTemplate(
                order=3,
                capability_id="filesystem.chmod",
                input_template="chmod 755 {executable_path}",
                purpose="Przywróć oczekiwany tryb pliku.",
            ),
            SolutionStepTemplate(
                order=4,
                capability_id="systemd.restart",
                input_template="systemctl restart {primary_service}",
                purpose="Uruchom usługę po przywróceniu pliku.",
            ),
        ),
        briefing_addition="Proces usługi kończy się natychmiast podczas uruchamiania.",
        forbidden_public_terms=("permission denied", "chmod", "uprawnienia pliku"),
    ),
)

FAULTS_BY_ID: Final = MappingProxyType(
    {template.component_id: template for template in FAULT_TEMPLATES}
)
