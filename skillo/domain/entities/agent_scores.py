from dataclasses import dataclass


@dataclass
class AgentScores:
    """Agent scoring results."""

    skills_score: float
    location_score: float
    experience_score: float
    preferences_score: float
    education_score: float
    explanation: str = ""
