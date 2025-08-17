from typing import List

from pydantic import BaseModel, Field

from skillo.domain.enums import MatchRecommendation
from skillo.domain.schemas import (
    DocumentProcessingResponse,
    EducationAnalysisResponse,
    ExperienceAnalysisResponse,
    LocationAnalysisResponse,
    NormalizationResponse,
    PreferencesAnalysisResponse,
    SkillsAnalysisResponse,
    SupervisorAnalysisResponse,
)


class SkillsAnalysisResponseAdapter(BaseModel):
    """Pydantic adapter for Skills Agent LangChain integration."""

    cv_skills: List[str] = Field(
        description="List of key skills extracted from CV"
    )
    required_skills: List[str] = Field(
        description="List of required skills from job posting"
    )
    matched_skills: List[str] = Field(
        description="List of skills that match between CV and job"
    )
    score: float = Field(
        ge=0.0, le=1.0, description="Skills match score between 0.0 and 1.0"
    )
    explanation: str = Field(
        description="Brief explanation of the skills match"
    )

    def to_domain(self) -> SkillsAnalysisResponse:
        """Convert to domain dataclass."""
        return SkillsAnalysisResponse(
            cv_skills=self.cv_skills,
            required_skills=self.required_skills,
            matched_skills=self.matched_skills,
            score=self.score,
            explanation=self.explanation,
        )


class LocationAnalysisResponseAdapter(BaseModel):
    """Pydantic adapter for Location Agent LangChain integration."""

    candidate_location: str = Field(
        description="Candidate's location or 'Not specified'"
    )
    job_location: str = Field(description="Job location or 'Not specified'")
    remote_work: str = Field(
        description="Remote work availability: Yes/No/Hybrid/Not specified"
    )
    distance_km: str = Field(description="Distance in km or 'Not calculated'")
    commute_feasibility: str = Field(description="Commute feasibility level")
    score: float = Field(
        ge=0.0, le=1.0, description="Location match score between 0.0 and 1.0"
    )
    explanation: str = Field(
        description="Detailed explanation including distance analysis and commute feasibility"
    )

    def to_domain(self) -> LocationAnalysisResponse:
        """Convert to domain dataclass."""
        return LocationAnalysisResponse(
            candidate_location=self.candidate_location,
            job_location=self.job_location,
            remote_work=self.remote_work,
            distance_km=self.distance_km,
            commute_feasibility=self.commute_feasibility,
            score=self.score,
            explanation=self.explanation,
        )


class ExperienceAnalysisResponseAdapter(BaseModel):
    """Pydantic adapter for Experience Agent LangChain integration."""

    cv_experience_years: str = Field(
        description="Years of experience from CV or 'Not specified'"
    )
    required_experience_years: str = Field(
        description="Required years of experience or 'Not specified'"
    )
    cv_level: str = Field(description="CV experience level")
    required_level: str = Field(description="Required experience level")
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Experience match score between 0.0 and 1.0",
    )
    explanation: str = Field(
        description="Brief explanation of the experience match"
    )

    def to_domain(self) -> ExperienceAnalysisResponse:
        """Convert to domain dataclass."""
        return ExperienceAnalysisResponse(
            cv_experience_years=self.cv_experience_years,
            required_experience_years=self.required_experience_years,
            cv_level=self.cv_level,
            required_level=self.required_level,
            score=self.score,
            explanation=self.explanation,
        )


class PreferencesAnalysisResponseAdapter(BaseModel):
    """Pydantic adapter for Preferences Agent LangChain integration."""

    cv_preferences: str = Field(
        description="Brief description of candidate preferences"
    )
    job_culture: str = Field(
        description="Brief description of company culture/work style"
    )
    work_style_match: str = Field(description="Work style compatibility level")
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Preferences match score between 0.0 and 1.0",
    )
    explanation: str = Field(
        description="Brief explanation of the preferences match"
    )

    def to_domain(self) -> PreferencesAnalysisResponse:
        """Convert to domain dataclass."""
        return PreferencesAnalysisResponse(
            cv_preferences=self.cv_preferences,
            job_culture=self.job_culture,
            work_style_match=self.work_style_match,
            score=self.score,
            explanation=self.explanation,
        )


class EducationAnalysisResponseAdapter(BaseModel):
    """Pydantic adapter for Education Agent LangChain integration."""

    cv_degree: str = Field(description="Candidate's highest degree level")
    cv_field: str = Field(
        description="Candidate's field of study or 'Not specified'"
    )
    required_degree: str = Field(description="Job required degree level")
    required_field: str = Field(
        description="Job required field of study or 'Not specified'"
    )
    certifications: str = Field(
        description="Relevant certifications mentioned"
    )
    degree_match: str = Field(
        description="How candidate degree compares to requirements"
    )
    score: float = Field(
        ge=0.0, le=1.0, description="Education match score between 0.0 and 1.0"
    )
    explanation: str = Field(
        description="Brief explanation of the education match"
    )

    def to_domain(self) -> EducationAnalysisResponse:
        """Convert to domain dataclass."""
        return EducationAnalysisResponse(
            cv_degree=self.cv_degree,
            cv_field=self.cv_field,
            required_degree=self.required_degree,
            required_field=self.required_field,
            certifications=self.certifications,
            degree_match=self.degree_match,
            score=self.score,
            explanation=self.explanation,
        )


class DocumentProcessingResponseAdapter(BaseModel):
    """Pydantic adapter for Document Processing Agent LangChain integration."""

    name: str = Field(
        description="Person name (CV) or Job title (Job posting)"
    )
    contact: str = Field(
        description="Contact info (CV) or Company name (Job posting)"
    )
    skills: List[str] = Field(
        description="List of skills/technical requirements"
    )
    experience: List[str] = Field(
        description="List of experience entries/requirements"
    )
    education: List[str] = Field(
        description="List of education entries/requirements"
    )
    location: str = Field(description="Location information")
    preferences: List[str] = Field(
        description="Work preferences/company culture aspects"
    )

    def to_domain(self) -> DocumentProcessingResponse:
        """Convert to domain dataclass."""
        return DocumentProcessingResponse(
            name=self.name,
            contact=self.contact,
            skills=self.skills,
            experience=self.experience,
            education=self.education,
            location=self.location,
            preferences=self.preferences,
        )


class NormalizationResponseAdapter(BaseModel):
    """Pydantic adapter for Normalization Agent LangChain integration."""

    normalized_job_title: str = Field(description="Standardized job title")
    normalized_location: str = Field(
        description="Standardized location format (City, Country)"
    )
    normalized_skills: List[str] = Field(
        description="Standardized skill names"
    )
    remote_work_status: str = Field(
        description="Standardized remote work status"
    )
    experience_level: str = Field(description="Standardized experience level")
    industry_sector: str = Field(description="Identified industry sector")
    explanation: str = Field(
        description="Summary of normalization changes made"
    )

    def to_domain(self) -> NormalizationResponse:
        """Convert to domain dataclass."""
        return NormalizationResponse(
            normalized_job_title=self.normalized_job_title,
            normalized_location=self.normalized_location,
            normalized_skills=self.normalized_skills,
            remote_work_status=self.remote_work_status,
            experience_level=self.experience_level,
            industry_sector=self.industry_sector,
            explanation=self.explanation,
        )


class SupervisorAnalysisResponseAdapter(BaseModel):
    """Pydantic adapter for Supervisor Agent LangChain integration."""

    skills_score: float = Field(
        ge=0.0, le=1.0, description="Skills analysis score"
    )
    location_score: float = Field(
        ge=0.0, le=1.0, description="Location analysis score"
    )
    experience_score: float = Field(
        ge=0.0, le=1.0, description="Experience analysis score"
    )
    preferences_score: float = Field(
        ge=0.0, le=1.0, description="Preferences analysis score"
    )
    education_score: float = Field(
        ge=0.0, le=1.0, description="Education analysis score"
    )
    weighted_final_score: float = Field(
        ge=0.0, le=1.0, description="Final weighted score"
    )
    recommendation: MatchRecommendation = Field(
        description="Overall recommendation level"
    )
    explanation: str = Field(
        description="Comprehensive explanation combining all agent analyses"
    )

    def to_domain(self) -> SupervisorAnalysisResponse:
        """Convert to domain dataclass."""
        return SupervisorAnalysisResponse(
            skills_score=self.skills_score,
            location_score=self.location_score,
            experience_score=self.experience_score,
            preferences_score=self.preferences_score,
            education_score=self.education_score,
            weighted_final_score=self.weighted_final_score,
            recommendation=self.recommendation,
            explanation=self.explanation,
        )
