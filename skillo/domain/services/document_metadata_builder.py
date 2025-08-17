from typing import Any, Dict, List, Optional

from skillo.domain.schemas import (
    DocumentProcessingResponse,
    NormalizationResponse,
)


class DocumentMetadataBuilder:
    """Domain service for building document metadata."""

    @staticmethod
    def build_base_metadata(
        filename: str,
        processing_response: DocumentProcessingResponse,
        normalization_response: NormalizationResponse,
        profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build common metadata fields for documents."""
        metadata = {
            "filename": filename,
            "name": processing_response.name,
            "job_title": normalization_response.normalized_job_title,
            "location": normalization_response.normalized_location,
            "skills": DocumentMetadataBuilder._join_skills(
                normalization_response.normalized_skills
            ),
            "experience": DocumentMetadataBuilder._join_experience(
                processing_response.experience
            ),
            "education": DocumentMetadataBuilder._join_education(
                processing_response.education
            ),
            "contact": processing_response.contact,
            "preferences": DocumentMetadataBuilder._join_preferences(
                processing_response.preferences
            ),
            "remote_work_status": normalization_response.remote_work_status,
            "experience_level": normalization_response.experience_level,
            "industry_sector": normalization_response.industry_sector,
        }

        if profile:
            metadata["profile"] = profile

        return metadata

    @staticmethod
    def _join_skills(skills: List[str]) -> str:
        """Join skills list to comma-separated string."""
        return ", ".join(skills) if skills else ""

    @staticmethod
    def _join_experience(experience: List[str]) -> str:
        """Join experience list to semicolon-separated string."""
        return "; ".join(experience) if experience else ""

    @staticmethod
    def _join_education(education: List[str]) -> str:
        """Join education list to semicolon-separated string."""
        return "; ".join(education) if education else ""

    @staticmethod
    def _join_preferences(preferences: List[str]) -> str:
        """Join preferences list to semicolon-separated string."""
        return "; ".join(preferences) if preferences else ""
