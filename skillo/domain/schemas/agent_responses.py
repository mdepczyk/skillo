from dataclasses import dataclass
from typing import List

from skillo.domain.enums import MatchRecommendation


@dataclass
class SkillsAnalysisResponse:
    """Domain response schema for Skills Agent analysis."""

    cv_skills: List[str]
    required_skills: List[str]
    matched_skills: List[str]
    score: float
    explanation: str


@dataclass
class LocationAnalysisResponse:
    """Domain response schema for Location Agent analysis."""

    candidate_location: str
    job_location: str
    remote_work: str
    distance_km: str
    commute_feasibility: str
    score: float
    explanation: str


@dataclass
class ExperienceAnalysisResponse:
    """Domain response schema for Experience Agent analysis."""

    cv_experience_years: str
    required_experience_years: str
    cv_level: str
    required_level: str
    score: float
    explanation: str


@dataclass
class PreferencesAnalysisResponse:
    """Domain response schema for Preferences Agent analysis."""

    cv_preferences: str
    job_culture: str
    work_style_match: str
    score: float
    explanation: str


@dataclass
class EducationAnalysisResponse:
    """Domain response schema for Education Agent analysis."""

    cv_degree: str
    cv_field: str
    required_degree: str
    required_field: str
    certifications: str
    degree_match: str
    score: float
    explanation: str


@dataclass
class SupervisorAnalysisResponse:
    """Domain response schema for Supervisor Agent comprehensive analysis."""

    skills_score: float
    location_score: float
    experience_score: float
    preferences_score: float
    education_score: float
    weighted_final_score: float
    recommendation: MatchRecommendation
    explanation: str


@dataclass
class DetailedMatchResult:
    """Comprehensive match result with all agent details."""

    skills_score: float
    location_score: float
    experience_score: float
    preferences_score: float
    education_score: float
    weighted_final_score: float
    recommendation: MatchRecommendation
    explanation: str


@dataclass
class DocumentProcessingResponse:
    """Domain response schema for Document Processing Agent."""

    name: str
    contact: str
    skills: List[str]
    experience: List[str]
    education: List[str]
    location: str
    preferences: List[str]


@dataclass
class NormalizationResponse:
    """Domain response schema for Normalization Agent."""

    normalized_job_title: str
    normalized_location: str
    normalized_skills: List[str]
    remote_work_status: str
    experience_level: str
    industry_sector: str
    explanation: str
