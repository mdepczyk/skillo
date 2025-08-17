from typing import List

from skillo.application.dto import DocumentDto, MatchResultDto
from skillo.domain.entities import Document, MatchResult
from skillo.domain.enums import DocumentType


class DTOMapper:
    """Centralized mapper for converting between domain entities and DTOs."""

    @staticmethod
    def document_to_dto(document: Document) -> DocumentDto:
        """Convert Domain Document to Application DTO."""
        return DocumentDto(
            id=document.id,
            document_type=document.document_type,
            content=document.content,
            metadata=document.metadata,
        )

    @staticmethod
    def dto_to_document(dto: DocumentDto) -> Document:
        """Convert DTO to domain entity."""
        return Document(
            id=dto.id,
            document_type=DocumentType(dto.document_type),
            content=dto.content,
            metadata=dto.metadata,
        )

    @staticmethod
    def match_result_to_dto(match_result: MatchResult) -> MatchResultDto:
        """Convert MatchResult to DTO."""
        if (
            match_result.cv_document is None
            or match_result.job_document is None
        ):
            raise ValueError(
                "MatchResult must have both cv_document and job_document"
            )

        return MatchResultDto(
            cv_id=match_result.cv_document.id,
            job_id=match_result.job_document.id,
            cv_filename=match_result.cv_document.metadata.get(
                "filename", "Unknown"
            ),
            job_filename=match_result.job_document.metadata.get(
                "filename", "Unknown"
            ),
            cv_metadata=match_result.cv_document.metadata,
            job_metadata=match_result.job_document.metadata,
            weighted_final_score=match_result.weighted_final_score,
            recommendation=match_result.recommendation.value,
            explanation=match_result.explanation,
            agent_scores={
                "skills": match_result.agent_scores.skills_score,
                "location": match_result.agent_scores.location_score,
                "experience": match_result.agent_scores.experience_score,
                "preferences": match_result.agent_scores.preferences_score,
                "education": match_result.agent_scores.education_score,
            },
            detailed_results=match_result.detailed_results or {},
        )

    @staticmethod
    def documents_to_dtos(documents: List[Document]) -> List[DocumentDto]:
        """Convert list of Documents to list of DTOs."""
        return [DTOMapper.document_to_dto(doc) for doc in documents]

    @staticmethod
    def match_results_to_dtos(
        match_results: List[MatchResult],
    ) -> List[MatchResultDto]:
        """Convert list of MatchResults to list of DTOs."""
        return [
            DTOMapper.match_result_to_dto(result) for result in match_results
        ]
