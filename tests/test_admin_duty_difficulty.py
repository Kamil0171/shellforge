from dataclasses import FrozenInstanceError

import pytest

from app.admin_duty.domain.difficulty import (
    BriefingDetailLevel,
    DifficultyLevel,
    NoiseLevel,
    ScoringSeverity,
    get_difficulty_profile,
)


def get_profiles():
    return [get_difficulty_profile(level) for level in DifficultyLevel]


def test_difficulty_has_exactly_three_supported_levels():
    assert [level.value for level in DifficultyLevel] == [
        "easy",
        "medium",
        "hard",
    ]


@pytest.mark.parametrize("level", list(DifficultyLevel))
def test_get_difficulty_profile_returns_matching_profile(level):
    assert get_difficulty_profile(level).level is level


@pytest.mark.parametrize(
    ("level", "expected_min_faults", "expected_max_faults"),
    [
        (DifficultyLevel.EASY, 1, 1),
        (DifficultyLevel.MEDIUM, 1, 1),
        (DifficultyLevel.HARD, 2, 2),
    ],
)
def test_fault_limits(level, expected_min_faults, expected_max_faults):
    profile = get_difficulty_profile(level)

    assert profile.min_faults == expected_min_faults
    assert profile.max_faults == expected_max_faults


def test_host_ranges_increase_with_difficulty():
    profiles = get_profiles()

    assert [(profile.min_hosts, profile.max_hosts) for profile in profiles] == [
        (2, 3),
        (3, 5),
        (5, 8),
    ]


def test_noise_increases_with_difficulty():
    assert [profile.noise_level for profile in get_profiles()] == [
        NoiseLevel.LOW,
        NoiseLevel.MEDIUM,
        NoiseLevel.HIGH,
    ]


def test_misleading_signal_limit_does_not_decrease():
    limits = [profile.misleading_signal_limit for profile in get_profiles()]

    assert limits == sorted(limits)


def test_hint_limit_does_not_increase():
    limits = [profile.hint_limit for profile in get_profiles()]

    assert limits == sorted(limits, reverse=True)


def test_briefing_becomes_less_detailed_with_difficulty():
    assert [profile.briefing_detail_level for profile in get_profiles()] == [
        BriefingDetailLevel.DETAILED,
        BriefingDetailLevel.BALANCED,
        BriefingDetailLevel.LIMITED,
    ]


def test_scoring_becomes_more_restrictive_with_difficulty():
    assert [profile.scoring_severity for profile in get_profiles()] == [
        ScoringSeverity.LENIENT,
        ScoringSeverity.STANDARD,
        ScoringSeverity.STRICT,
    ]


def test_difficulty_profiles_are_immutable():
    profile = get_difficulty_profile(DifficultyLevel.EASY)

    with pytest.raises(FrozenInstanceError):
        profile.hint_limit = 99


def test_unsupported_difficulty_does_not_use_fallback():
    with pytest.raises(ValueError, match="Nieobsługiwany poziom trudności"):
        get_difficulty_profile("unsupported")
