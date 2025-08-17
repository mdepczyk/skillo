from typing import List, Optional

from pydantic import BaseModel, Field

from skillo.domain.enums import (
    CommuteFeasibility,
    EducationLevel,
    EducationMatch,
    ExperienceLevel,
    MatchRecommendation,
    RemoteWorkStatus,
    WorkStyleMatch,
)


class SkillsAnalysisResponse(BaseModel):
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


class LocationAnalysisResponse(BaseModel):
    """Response schema for Location Agent analysis"""

    candidate_location: str = Field(
        description="Candidate's location or 'Not specified'"
    )
    job_location: str = Field(description="Job location or 'Not specified'")
    remote_work: str = Field(
        description="Remote work availability: Yes/No/Hybrid/Not specified"
    )
    distance_km: str = Field(description="Distance in km or 'Not calculated'")
    commute_feasibility: CommuteFeasibility = Field(
        description="Commute feasibility level"
    )
    score: float = Field(
        ge=0.0, le=1.0, description="Location match score between 0.0 and 1.0"
    )
    explanation: str = Field(
        description="Detailed explanation including distance analysis and commute feasibility"
    )


class ExperienceAnalysisResponse(BaseModel):
    """Response schema for Experience Agent analysis"""

    cv_experience_years: str = Field(
        description="Years of experience from CV or 'Not specified'"
    )
    required_experience_years: str = Field(
        description="Required years of experience or 'Not specified'"
    )
    cv_level: ExperienceLevel = Field(description="CV experience level")
    required_level: ExperienceLevel = Field(
        description="Required experience level"
    )
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Experience match score between 0.0 and 1.0",
    )
    explanation: str = Field(
        description="Brief explanation of the experience match"
    )


class PreferencesAnalysisResponse(BaseModel):
    """Response schema for Preferences Agent analysis"""

    cv_preferences: str = Field(
        description="Brief description of candidate preferences"
    )
    job_culture: str = Field(
        description="Brief description of company culture/work style"
    )
    work_style_match: WorkStyleMatch = Field(
        description="Work style compatibility level"
    )
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Preferences match score between 0.0 and 1.0",
    )
    explanation: str = Field(
        description="Brief explanation of the preferences match"
    )


class EducationAnalysisResponse(BaseModel):
    """Response schema for Education Agent analysis"""

    cv_degree: EducationLevel = Field(
        description="Candidate's highest degree level"
    )
    cv_field: str = Field(
        description="Candidate's field of study or 'Not specified'"
    )
    required_degree: EducationLevel = Field(
        description="Job required degree level"
    )
    required_field: str = Field(
        description="Job required field of study or 'Not specified'"
    )
    certifications: str = Field(
        description="Relevant certifications mentioned"
    )
    degree_match: EducationMatch = Field(
        description="How candidate degree compares to requirements"
    )
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Education match score between 0.0 and 1.0",
    )
    explanation: str = Field(
        description="Brief explanation of the education match"
    )


class SupervisorAnalysisResponse(BaseModel):
    """Response schema for Supervisor Agent comprehensive analysis"""

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


class AgentWeights(BaseModel):
    """Agent scoring weights configuration"""

    skills_weight: float = Field(
        ge=0.0, le=1.0, description="Weight for skills analysis"
    )
    location_weight: float = Field(
        ge=0.0, le=1.0, description="Weight for location analysis"
    )
    experience_weight: float = Field(
        ge=0.0, le=1.0, description="Weight for experience analysis"
    )
    preferences_weight: float = Field(
        ge=0.0, le=1.0, description="Weight for preferences analysis"
    )
    education_weight: float = Field(
        ge=0.0, le=1.0, description="Weight for education analysis"
    )


class DetailedMatchResult(BaseModel):
    """Comprehensive match result with all agent details"""

    skills_score: float = Field(ge=0.0, le=1.0)
    location_score: float = Field(ge=0.0, le=1.0)
    experience_score: float = Field(ge=0.0, le=1.0)
    preferences_score: float = Field(ge=0.0, le=1.0)
    education_score: float = Field(ge=0.0, le=1.0)
    weighted_final_score: float = Field(ge=0.0, le=1.0)

    recommendation: MatchRecommendation = Field(
        description="Overall match recommendation"
    )
    explanation: str = Field(description="Comprehensive explanation")
    agent_weights: AgentWeights = Field(description="Weights used for scoring")

    skills_details: Optional[SkillsAnalysisResponse] = None
    location_details: Optional[LocationAnalysisResponse] = None
    experience_details: Optional[ExperienceAnalysisResponse] = None
    preferences_details: Optional[PreferencesAnalysisResponse] = None
    education_details: Optional[EducationAnalysisResponse] = None


class DocumentProcessingResponse(BaseModel):
    """Response schema for Document Processing Agent"""

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


class NormalizationResponse(BaseModel):
    """Response schema for Normalization Agent"""

    normalized_job_title: str = Field(description="Standardized job title")
    normalized_location: str = Field(
        description="Standardized location format (City, Country)"
    )
    normalized_skills: List[str] = Field(
        description="Standardized skill names"
    )
    remote_work_status: RemoteWorkStatus = Field(
        description="Standardized remote work status"
    )
    experience_level: ExperienceLevel = Field(
        description="Standardized experience level"
    )
    industry_sector: str = Field(description="Identified industry sector")
    explanation: str = Field(
        description="Summary of normalization changes made"
    )


class AgentRoutingResponse(BaseModel):
    """Pydantic model for structured LLM routing response."""

    agents: List[str] = Field(description="List of agent names to invoke")
    reasoning: str = Field(description="Explanation of routing decisions")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in routing decision"
    )
    priority: str = Field(
        default="normal", description="Priority level: low, normal, high"
    )
