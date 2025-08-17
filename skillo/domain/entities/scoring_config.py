from dataclasses import dataclass


@dataclass
class ScoringConfig:
    """Scoring weights configuration - replaces scattered config values."""

    skills_weight: float = 0.3
    experience_weight: float = 0.25
    education_weight: float = 0.2
    location_weight: float = 0.15
    preferences_weight: float = 0.1
