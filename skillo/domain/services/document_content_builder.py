from skillo.domain.schemas import (
    DocumentProcessingResponse,
    NormalizationResponse,
)


class DocumentContentBuilder:
    """Domain service for building document content."""

    @staticmethod
    def build_cv_content(
        processing_response: DocumentProcessingResponse,
        normalization_response: NormalizationResponse,
    ) -> str:
        """Build CV content for vectorization and search."""
        content_parts = [
            f"Job Title: {normalization_response.normalized_job_title}",
            f"Skills: {', '.join(normalization_response.normalized_skills)}",
            f"Experience Level: {normalization_response.experience_level}",
            f"Industry: {normalization_response.industry_sector}",
        ]

        if processing_response.experience:
            content_parts.append(
                f"Experience Details: {'; '.join(processing_response.experience)}"
            )

        if processing_response.education:
            content_parts.append(
                f"Education: {'; '.join(processing_response.education)}"
            )

        if processing_response.preferences:
            content_parts.append(
                f"Preferences: {'; '.join(processing_response.preferences)}"
            )

        return "\n".join(content_parts)

    @staticmethod
    def build_job_content(
        processing_response: DocumentProcessingResponse,
        normalization_response: NormalizationResponse,
    ) -> str:
        """Build job content for vectorization and search."""
        content_parts = [
            f"Job Title: {normalization_response.normalized_job_title}",
            f"Required Skills: {', '.join(normalization_response.normalized_skills)}",
            f"Experience Level: {normalization_response.experience_level}",
            f"Industry: {normalization_response.industry_sector}",
        ]

        if processing_response.experience:
            content_parts.append(
                f"Requirements: {'; '.join(processing_response.experience)}"
            )

        if processing_response.preferences:
            content_parts.append(
                f"Culture: {'; '.join(processing_response.preferences)}"
            )

        return "\n".join(content_parts)
