from types import MappingProxyType
from typing import Final

from app.admin_duty.components.models import (
    ComponentMetadata,
    EnvironmentTemplate,
    ResourceBinding,
    ResourceRole,
)
from app.admin_duty.domain.definition import DataField, ResourceType, WorldResource
from app.admin_duty.domain.difficulty import DifficultyLevel

COMPONENT_VERSION = "1.0"


def _environment(
    *,
    component_id: str,
    label: str,
    description: str,
    organization: str,
    environment_label: str,
    title: str,
    briefing: str,
    main_objective: str,
    ticket_prefix: str,
    map_component_id: str,
    primary_host_id: str,
    primary_hostname: str,
    support_host_id: str,
    support_hostname: str,
    support_role: str,
    service_id: str,
    service_name: str,
    executable_file_id: str,
    exec_target: str,
    broken_exec_target: str,
    environment_variable: str,
    environment_value: str,
) -> EnvironmentTemplate:
    return EnvironmentTemplate(
        component_id=component_id,
        version=COMPONENT_VERSION,
        metadata=ComponentMetadata(label=label, description=description),
        compatible_difficulties=(DifficultyLevel.EASY,),
        organization=organization,
        environment_label=environment_label,
        title=title,
        briefing=briefing,
        main_objective=main_objective,
        ticket_prefix=ticket_prefix,
        tags=("systemd", "diagnostyka", "easy"),
        map_component_id=map_component_id,
        resources=(
            WorldResource(
                resource_id=primary_host_id,
                resource_type=ResourceType.HOST,
                state="running",
                attributes=(
                    DataField(key="role", value="application"),
                    DataField(key="hostname", value=primary_hostname),
                ),
            ),
            WorldResource(
                resource_id=support_host_id,
                resource_type=ResourceType.HOST,
                state="running",
                attributes=(
                    DataField(key="role", value=support_role),
                    DataField(key="hostname", value=support_hostname),
                ),
            ),
            WorldResource(
                resource_id=executable_file_id,
                resource_type=ResourceType.FILE,
                state="present",
                parent_id=primary_host_id,
                attributes=(
                    DataField(key="current_mode", value="0755"),
                    DataField(key="expected_mode", value="0755"),
                    DataField(key="owner", value="app"),
                ),
            ),
            WorldResource(
                resource_id=service_id,
                resource_type=ResourceType.SERVICE,
                state="running",
                parent_id=primary_host_id,
                dependencies=(executable_file_id,),
                attributes=(
                    DataField(key="manager", value="systemd"),
                    DataField(key="service_name", value=service_name),
                    DataField(key="configured_exec_start", value=exec_target),
                    DataField(key="expected_exec_start", value=exec_target),
                    DataField(key="executable_resource_id", value=executable_file_id),
                    DataField(
                        key="required_environment_variable",
                        value=environment_variable,
                    ),
                    DataField(
                        key="expected_environment_value",
                        value=environment_value,
                    ),
                    DataField(
                        key=f"environment.{environment_variable}",
                        value=environment_value,
                    ),
                ),
            ),
        ),
        bindings=(
            ResourceBinding(
                role=ResourceRole.PRIMARY_HOST, resource_id=primary_host_id
            ),
            ResourceBinding(
                role=ResourceRole.SUPPORT_HOST, resource_id=support_host_id
            ),
            ResourceBinding(role=ResourceRole.PRIMARY_SERVICE, resource_id=service_id),
            ResourceBinding(
                role=ResourceRole.EXECUTABLE_FILE,
                resource_id=executable_file_id,
            ),
        ),
        context=(
            DataField(key="expected_exec_target", value=exec_target),
            DataField(key="broken_exec_target", value=broken_exec_target),
            DataField(key="environment_variable", value=environment_variable),
            DataField(key="environment_value", value=environment_value),
            DataField(key="expected_file_mode", value="0755"),
            DataField(key="broken_file_mode", value="0644"),
        ),
    )


ENVIRONMENT_TEMPLATES = (
    _environment(
        component_id="web-application",
        label="Aplikacja webowa",
        description="Publiczne API i monitoring na osobnych hostach.",
        organization="Northstar Commerce",
        environment_label="Platforma sprzedażowa",
        title="Niedostępność API platformy",
        briefing="Monitoring zgłasza niedostępność głównego API platformy.",
        main_objective="Przywróć usługę service-api do stanu running.",
        ticket_prefix="WEB",
        map_component_id="web-operations-room",
        primary_host_id="host-app-01",
        primary_hostname="app-01",
        support_host_id="host-monitoring-01",
        support_hostname="monitoring-01",
        support_role="monitoring",
        service_id="service-api",
        service_name="example-api.service",
        executable_file_id="file-api-binary",
        exec_target="api-server",
        broken_exec_target="legacy-api-server",
        environment_variable="DATABASE_URL",
        environment_value="database-primary",
    ),
    _environment(
        component_id="internal-business-service",
        label="Wewnętrzny system biznesowy",
        description="Usługa przetwarzająca zadania i dedykowany host bazy danych.",
        organization="Vistula Logistics",
        environment_label="System obsługi zleceń",
        title="Zatrzymane przetwarzanie zleceń",
        briefing="Kolejka zleceń rośnie, a worker nie przetwarza nowych zadań.",
        main_objective="Przywróć usługę service-worker do stanu running.",
        ticket_prefix="BIZ",
        map_component_id="business-service-room",
        primary_host_id="host-business-01",
        primary_hostname="business-01",
        support_host_id="host-database-01",
        support_hostname="database-01",
        support_role="database",
        service_id="service-worker",
        service_name="orders-worker.service",
        executable_file_id="file-worker-binary",
        exec_target="orders-worker",
        broken_exec_target="legacy-worker",
        environment_variable="QUEUE_URL",
        environment_value="queue-primary",
    ),
    _environment(
        component_id="reverse-proxy-stack",
        label="Stos reverse proxy",
        description="Warstwa brzegowa obsługująca ruch do aplikacji wewnętrznej.",
        organization="Baltic Media Network",
        environment_label="Warstwa dostępu brzegowego",
        title="Przerwa w obsłudze ruchu brzegowego",
        briefing="Użytkownicy otrzymują błędy podczas połączenia z aplikacją.",
        main_objective="Przywróć usługę service-proxy do stanu running.",
        ticket_prefix="EDGE",
        map_component_id="edge-operations-room",
        primary_host_id="host-edge-01",
        primary_hostname="edge-01",
        support_host_id="host-backend-01",
        support_hostname="backend-01",
        support_role="application",
        service_id="service-proxy",
        service_name="example-proxy.service",
        executable_file_id="file-proxy-binary",
        exec_target="edge-proxy",
        broken_exec_target="old-edge-proxy",
        environment_variable="UPSTREAM_URL",
        environment_value="backend-primary",
    ),
)

ENVIRONMENTS_BY_ID: Final = MappingProxyType(
    {template.component_id: template for template in ENVIRONMENT_TEMPLATES}
)
