from app.admin_duty.domain.definition import IncidentPresentation, ObjectiveType

PUBLIC_OBJECTIVES = {
    ObjectiveType.CONFIRM_SYMPTOM: "Potwierdź objaw zgłoszonej niedostępności.",
    ObjectiveType.INSPECT_SERVICE: "Sprawdź stan usługi i jej logi.",
    ObjectiveType.IDENTIFY_DEPENDENCY: "Sprawdź zależności usługi.",
    ObjectiveType.RESTORE_DEPENDENCY: "Przywróć poprawne działanie usługi.",
    ObjectiveType.VERIFY_SERVICE: "Zweryfikuj stan usługi po zmianach.",
    ObjectiveType.VERIFY_END_TO_END: "Potwierdź dostępność całej ścieżki żądania.",
}


def protect_public_narrative(draft):
    presentation = IncidentPresentation(
        title="Niedostępność aplikacji",
        organization="Centrum operacyjne",
        environment_label="Środowisko usług Linux",
        briefing=(
            "Monitoring zgłasza niedostępność aplikacji. Sprawdź stan usług, "
            "zbierz dane diagnostyczne i przywróć poprawne działanie środowiska."
        ),
        main_objective="Przywróć dostępność aplikacji i potwierdź wynik diagnostyką.",
        tags=("diagnostyka", "network"),
        estimated_time_minutes=15 if draft.difficulty.value == "easy" else 25,
    )
    return draft.model_copy(update={
        "presentation": presentation,
        "objectives": tuple(
            objective.model_copy(update={"label": PUBLIC_OBJECTIVES[objective.objective_type]})
            for objective in draft.objectives
        ),
        "initial_world_state": draft.initial_world_state.model_copy(update={
            "resources": tuple(
                resource.model_copy(update={
                    "attributes": tuple(
                        field.model_copy(update={"value": "Serwer Linux"})
                        if field.key == "role" else field
                        for field in resource.attributes
                    ),
                })
                for resource in draft.initial_world_state.resources
            ),
        }),
    })
