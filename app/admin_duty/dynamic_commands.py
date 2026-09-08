from pydantic import Field

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
    IncidentDefinition,
    ResourceType,
)
from app.admin_duty.domain.progress import SessionProgress
from app.admin_duty.domain.runtime import RuntimeResource, SessionRuntimeState

SYSTEMD_MANAGER = "systemd"


class CommandExecutionError(ValueError):
    pass


class VirtualEditorAction(FrozenDomainModel):
    path: str = Field(min_length=1, max_length=1024)
    content: str = Field(max_length=32768)


class CommandExecutionResult(FrozenDomainModel):
    output: str = Field(max_length=1000)
    success: bool
    current_working_directory: str = Field(
        default="/home/operator", min_length=1, max_length=1024
    )
    prompt: str = Field(default="operator@incident:~$", min_length=1, max_length=1200)
    editor: VirtualEditorAction | None = None
    progress: SessionProgress


def _get_systemd_service(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    capability_id: Identifier,
) -> RuntimeResource:
    if definition.scenario_id != state.scenario_id:
        raise CommandExecutionError(
            "Definicja incydentu i sesja mają różne scenario_id."
        )

    if capability_id not in definition.capabilities.command_capability_ids:
        raise CommandExecutionError(
            f"Scenariusz nie udostępnia capability {capability_id}."
        )

    resource = state.world_state.resources.get(resource_id)

    if resource is None:
        normalized = resource_id.removesuffix(".service")
        resource = next(
            (
                candidate
                for candidate in state.world_state.resources.values()
                if candidate.resource_type is ResourceType.SERVICE
                and isinstance(candidate.attributes.get("service_name"), str)
                and candidate.attributes["service_name"].removesuffix(".service")
                == normalized
            ),
            None,
        )

    if resource is None:
        raise CommandExecutionError(f"Zasób runtime nie istnieje: {resource_id}.")

    if resource.resource_type is not ResourceType.SERVICE:
        raise CommandExecutionError(f"Zasób {resource_id} nie jest usługą.")

    if resource.parent_resource_id != state.active_host_id:
        raise CommandExecutionError(
            f"Usługa {resource_id} działa na innym hoście. Użyj ssh <host>."
        )

    if resource.attributes.get("manager") != SYSTEMD_MANAGER:
        raise CommandExecutionError(
            f"Usługa {resource_id} nie jest zarządzana przez systemd."
        )

    return resource
