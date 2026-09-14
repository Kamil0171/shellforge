from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final


class DifficultyLevel(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class NoiseLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BriefingDetailLevel(StrEnum):
    DETAILED = "detailed"
    BALANCED = "balanced"
    LIMITED = "limited"


class ScoringSeverity(StrEnum):
    LENIENT = "lenient"
    STANDARD = "standard"
    STRICT = "strict"


@dataclass(frozen=True, slots=True)
class DifficultyProfile:
    level: DifficultyLevel
    min_hosts: int
    max_hosts: int
    min_faults: int
    max_faults: int
    noise_level: NoiseLevel
    misleading_signal_limit: int
    hint_limit: int
    briefing_detail_level: BriefingDetailLevel
    scoring_severity: ScoringSeverity


_DIFFICULTY_PROFILES: Final[Mapping[DifficultyLevel, DifficultyProfile]] = (
    MappingProxyType(
        {
            DifficultyLevel.EASY: DifficultyProfile(
                level=DifficultyLevel.EASY,
                min_hosts=2,
                max_hosts=3,
                min_faults=1,
                max_faults=1,
                noise_level=NoiseLevel.LOW,
                misleading_signal_limit=0,
                hint_limit=3,
                briefing_detail_level=BriefingDetailLevel.DETAILED,
                scoring_severity=ScoringSeverity.LENIENT,
            ),
            DifficultyLevel.MEDIUM: DifficultyProfile(
                level=DifficultyLevel.MEDIUM,
                min_hosts=3,
                max_hosts=5,
                min_faults=1,
                max_faults=1,
                noise_level=NoiseLevel.MEDIUM,
                misleading_signal_limit=1,
                hint_limit=2,
                briefing_detail_level=BriefingDetailLevel.BALANCED,
                scoring_severity=ScoringSeverity.STANDARD,
            ),
            DifficultyLevel.HARD: DifficultyProfile(
                level=DifficultyLevel.HARD,
                min_hosts=5,
                max_hosts=8,
                min_faults=2,
                max_faults=2,
                noise_level=NoiseLevel.HIGH,
                misleading_signal_limit=3,
                hint_limit=1,
                briefing_detail_level=BriefingDetailLevel.LIMITED,
                scoring_severity=ScoringSeverity.STRICT,
            ),
        }
    )
)


def get_difficulty_profile(level: DifficultyLevel) -> DifficultyProfile:
    if not isinstance(level, DifficultyLevel):
        raise ValueError(f"Nieobsługiwany poziom trudności: {level!r}")

    try:
        return _DIFFICULTY_PROFILES[level]
    except KeyError as exc:
        raise ValueError(f"Nieobsługiwany poziom trudności: {level!r}") from exc
