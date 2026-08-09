from copy import deepcopy

from app.admin_duty.scenarios.incident_001 import SCENARIO


def create_scenario_state() -> dict:
    state = deepcopy(SCENARIO["initial_state"])
    state["filesystem"] = deepcopy(SCENARIO["filesystem"])

    return state


def penalize(state: dict, points: int) -> None:
    state["score"] = max(0, state["score"] - points)


def mark_command_used(
    state: dict,
    cost: int = 5,
) -> None:
    state["commands_used"] += 1

    if cost:
        penalize(state, cost)


def is_mission_complete(state: dict) -> bool:
    return (
        state["configuration_fixed"]
        and state["daemon_reloaded"]
        and state["service_running"]
        and state["portal_verified"]
    )


def get_objectives(state: dict) -> list[dict]:
    completion = {
        "check_portal": state["portal_checked"],
        "identify_layer": state["service_checked"],
        "find_cause": state["cause_identified"],
        "restore_service": state["service_running"],
        "verify_portal": state["portal_verified"],
    }

    return [
        {
            "key": objective["key"],
            "label": objective["label"],
            "completed": completion[objective["key"]],
        }
        for objective in SCENARIO["objectives"]
    ]


def get_progress(state: dict) -> dict:
    mission_complete = is_mission_complete(state)

    if mission_complete:
        state["mission_complete"] = True

    return {
        "score": state["score"],
        "commands_used": state["commands_used"],
        "hints_used": state["hints_used"],
        "solution_viewed": state["solution_viewed"],
        "mission_complete": mission_complete,
        "objectives": get_objectives(state),
    }


def reveal_next_hint(state: dict) -> dict:
    hint_index = state["hints_used"]

    if hint_index >= len(SCENARIO["hints"]):
        return {
            "available": False,
            "message": "Wykorzystano już wszystkie podpowiedzi.",
            "progress": get_progress(state),
        }

    hint = SCENARIO["hints"][hint_index]

    penalize(state, hint["cost"])
    state["hints_used"] += 1

    return {
        "available": True,
        "number": state["hints_used"],
        "cost": hint["cost"],
        "text": hint["text"],
        "progress": get_progress(state),
    }


def reveal_solution(state: dict) -> dict:
    if not state["solution_viewed"]:
        state["solution_viewed"] = True

        penalize(state, 250)

        state["score"] = min(
            state["score"],
            500,
        )

    return {
        "steps": SCENARIO["solution"],
        "progress": get_progress(state),
    }
