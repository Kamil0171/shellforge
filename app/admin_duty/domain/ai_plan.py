import json
from typing import Literal

from pydantic import Field, model_validator

from app.admin_duty.components.scenarios.hard import (
    HARD_COMBINATIONS,
    HARD_DEPENDENCY_ARCHETYPE,
    HARD_ENVIRONMENT_ARCHETYPE,
    HARD_SYMPTOM_ARCHETYPE,
    get_hard_combination_for_pair,
)
from app.admin_duty.domain.definition import FrozenDomainModel
from app.admin_duty.domain.generation import DraftValidationError

EASY_FAULTS = (
    "systemd-service-failed",
    "systemd-wrong-exec-start",
    "systemd-missing-environment-variable",
    "systemd-permission-denied",
)
MEDIUM_FAULTS = (
    "dependency-firewall-blocked",
    "dependency-package-missing",
    "selinux-context-invalid",
    "networkmanager-dns-invalid",
    "external-firewall-mismatch",
)
EASY_ENVIRONMENTS = {
    "web-application": ("web-api", "web-operations-room"),
    "internal-business-service": ("worker", "business-service-room"),
    "reverse-proxy-stack": ("reverse-proxy", "edge-operations-room"),
}
SYMPTOMS = {
    "systemd-service-failed": "service_unavailable",
    "systemd-wrong-exec-start": "service_start_failure",
    "systemd-missing-environment-variable": "configuration_failure",
    "systemd-permission-denied": "execution_failure",
    **dict.fromkeys(MEDIUM_FAULTS, "public_service_degraded"),
}
SKILLS = ("systemd", "filesystem", "network", "firewall", "packages", "selinux", "dns")

HARD_FAULTS = tuple(
    dict.fromkeys(
        category
        for combination in HARD_COMBINATIONS
        for category in (
            combination.primary_fault_category,
            combination.secondary_fault_category,
        )
    )
)


class AIIncidentPlan(FrozenDomainModel):
    difficulty: Literal["easy", "medium", "hard"]
    environment_archetype: Literal[
        "web-application",
        "internal-business-service",
        "reverse-proxy-stack",
        "web-stack",
        "hard-web-stack",
    ]
    fault_category: Literal[
        "systemd-service-failed",
        "systemd-wrong-exec-start",
        "systemd-missing-environment-variable",
        "systemd-permission-denied",
        "dependency-firewall-blocked",
        "dependency-package-missing",
        "selinux-context-invalid",
        "networkmanager-dns-invalid",
        "external-firewall-mismatch",
    ] | None = None
    primary_fault_category: Literal[
        "dependency-firewall-blocked",
        "selinux-context-invalid",
        "networkmanager-dns-invalid",
        "external-firewall-mismatch",
        "dependency-package-missing",
        "systemd-wrong-exec-start",
        "service-config-invalid",
        "dependency-port-mismatch",
        "networkmanager-connection-inactive",
    ] | None = None
    secondary_fault_category: Literal[
        "dependency-firewall-blocked",
        "selinux-context-invalid",
        "networkmanager-dns-invalid",
        "external-firewall-mismatch",
        "dependency-package-missing",
        "systemd-wrong-exec-start",
        "service-config-invalid",
        "dependency-port-mismatch",
        "networkmanager-connection-inactive",
    ] | None = None
    affected_service_archetype: Literal["web-api", "worker", "reverse-proxy"]
    dependency_archetype: Literal["direct-service", "proxy-api-database"]
    symptom_archetype: Literal[
        "service_unavailable",
        "service_start_failure",
        "configuration_failure",
        "execution_failure",
        "public_service_degraded",
        "progressive_service_degradation",
    ]
    lesson_id: int | None = Field(default=None, ge=1)
    skill_tags: tuple[
        Literal[
            "systemd",
            "filesystem",
            "network",
            "firewall",
            "packages",
            "selinux",
            "dns",
        ],
        ...,
    ] = Field(default=(), max_length=3)
    seed: int = Field(ge=0, le=2**63 - 1)

    @model_validator(mode="after")
    def supported_combination(self):
        if len(self.skill_tags) != len(set(self.skill_tags)):
            raise ValueError("Powtórzony skill tag.")
        if self.difficulty == "hard":
            if self.fault_category is not None:
                raise ValueError("HARD nie używa pola fault_category.")
            if (
                self.primary_fault_category is None
                or self.secondary_fault_category is None
            ):
                raise ValueError("HARD wymaga primary i secondary fault.")
            try:
                combination = get_hard_combination_for_pair(
                    self.primary_fault_category,
                    self.secondary_fault_category,
                )
            except ValueError as error:
                raise ValueError("Nieobsługiwana para faultów HARD.") from error
            valid = (
                self.environment_archetype
                in combination.compatible_environment_archetypes
                and self.affected_service_archetype
                == combination.affected_service_archetype
                and self.dependency_archetype == combination.dependency_archetype
                and self.symptom_archetype == HARD_SYMPTOM_ARCHETYPE
                and set(self.skill_tags) <= set(combination.skill_tags)
            )
            if not valid:
                raise ValueError("Nieobsługiwana kombinacja archetypów HARD.")
            return self
        if self.primary_fault_category is not None or self.secondary_fault_category is not None:
            raise ValueError("EASY i MEDIUM nie obsługują secondary fault.")
        if self.fault_category is None:
            raise ValueError("EASY i MEDIUM wymagają fault_category.")
        if self.difficulty == "easy":
            environment = EASY_ENVIRONMENTS.get(self.environment_archetype)
            valid = (
                environment is not None
                and self.fault_category in EASY_FAULTS
                and self.affected_service_archetype == environment[0]
                and self.dependency_archetype == "direct-service"
            )
        else:
            service = (
                "reverse-proxy"
                if self.fault_category == "external-firewall-mismatch"
                else "web-api"
            )
            valid = (
                self.environment_archetype == "web-stack"
                and self.fault_category in MEDIUM_FAULTS
                and self.affected_service_archetype == service
                and self.dependency_archetype == "proxy-api-database"
            )
        if not valid or self.symptom_archetype != SYMPTOMS[self.fault_category]:
            raise ValueError("Nieobsługiwana kombinacja archetypów.")
        return self


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Powtórzony klucz JSON.")
        result[key] = value
    return result


def parse_ai_plan(payload) -> AIIncidentPlan:
    try:
        if isinstance(payload, AIIncidentPlan):
            payload = payload.model_dump_json()
        if isinstance(payload, (str, bytes)):
            if len(payload) > 8192:
                raise ValueError("Zbyt duży plan.")
            payload = json.loads(payload, object_pairs_hook=unique_json_object)
        return AIIncidentPlan.model_validate_json(
            json.dumps(payload, allow_nan=False), strict=True
        )
    except (ValueError, TypeError, RecursionError):
        pass
    raise DraftValidationError("Plan AI nie przeszedł walidacji.", category="plan")


def get_plan_capability_catalog(request):
    easy = request.difficulty.value == "easy"
    hard = request.difficulty.value == "hard"
    if hard:
        combinations = tuple(
            item
            for item in HARD_COMBINATIONS
            if (
                not request.environment_preferences
                or HARD_ENVIRONMENT_ARCHETYPE in request.environment_preferences
            )
            and (
                not request.allowed_fault_categories
                or {
                    item.primary_fault_category,
                    item.secondary_fault_category,
                }
                <= set(request.allowed_fault_categories)
            )
        )
        return {
            "environments_and_services": {
                HARD_ENVIRONMENT_ARCHETYPE: tuple(
                    dict.fromkeys(
                        item.affected_service_archetype for item in combinations
                    )
                )
            },
            "hard_pairs": tuple(
                {
                    "primary": item.primary_fault_category,
                    "secondary": item.secondary_fault_category,
                    "service": item.affected_service_archetype,
                    "skills": item.skill_tags,
                }
                for item in combinations
            ),
            "dependency": HARD_DEPENDENCY_ARCHETYPE,
            "symptom": HARD_SYMPTOM_ARCHETYPE,
            "skills": SKILLS,
            "hosts": [5, 5],
            "fault_count": 2,
        }
    environments = (
        {
            key: value[0]
            for key, value in EASY_ENVIRONMENTS.items()
            if request.map_id in {None, value[1]}
        }
        if easy
        else {"web-stack": "web-api"}
    )
    if easy and request.environment_preferences:
        preferred = {
            key: value
            for key, value in environments.items()
            if key in request.environment_preferences
        }
        environments = preferred or environments
    faults = EASY_FAULTS if easy else MEDIUM_FAULTS
    faults = tuple(
        fault
        for fault in faults
        if not request.allowed_fault_categories
        or fault in request.allowed_fault_categories
    )
    return {
        "environments_and_services": environments,
        "faults_and_symptoms": {fault: SYMPTOMS[fault] for fault in faults},
        "dependency": "direct-service" if easy else "proxy-api-database",
        "external_firewall_service": "reverse-proxy" if not easy else None,
        "skills": SKILLS,
        "hosts": [2, 2] if easy else [3, 4],
        "fault_count": 1,
    }
