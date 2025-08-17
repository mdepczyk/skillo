from typing import List

from skillo.application.dto import DocumentDto, MatchResultDto
from skillo.domain.entities import Document, MatchResult
from skillo.domain.enums import DocumentType
from skillo.domain.events import (
    EventPublisher,
    MatchingCompletedEvent,
    MatchingFailedEvent,
)
from skillo.domain.repositories import DocumentRepository
from skillo.domain.services import (
    MatchingService,
    SupervisorAgentInterface,
)


class MatchCVToJobs:
    """Match CV against available jobs."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        supervisor_agent: SupervisorAgentInterface,
        top_candidates_count: int,
        min_match_score: float,
        event_publisher: EventPublisher,
    ):
        """Initialize with dependencies."""
        self._document_repository = document_repository
        self._event_publisher = event_publisher

        self._matching_service = MatchingService(
            document_repository=document_repository,
            supervisor_agent=supervisor_agent,
            top_candidates_count=top_candidates_count,
            min_match_score=min_match_score,
        )

    def execute(self, cv_document: Document) -> List[MatchResult]:
        """Execute CV to jobs matching workflow."""
        try:
            matches = self._matching_service.match_cv_to_all_jobs(cv_document)

            if matches:
                event = MatchingCompletedEvent(
                    message=f"Found {len(matches)} job matches for {cv_document.metadata.get('filename', 'Unknown')}",
                    context="CV to Jobs Matching",
                    result_count=len(matches),
                )
            else:
                event = MatchingCompletedEvent(
                    message=f"No job matches found for {cv_document.metadata.get('filename', 'Unknown')}",
                    context="CV to Jobs Matching",
                    result_count=0,
                )

            self._event_publisher.publish(event)

            return matches

        except Exception as e:
            error_msg = f"CV matching workflow failed: {str(e)}"
            event = MatchingFailedEvent(
                error_message=error_msg,
                context="CV to Jobs Matching",
                exception_type=type(e).__name__,
            )
            self._event_publisher.publish(event)
            return []

    def execute_dto(
        self, cv_document_dto: DocumentDto
    ) -> List[MatchResultDto]:
        """Execute CV to jobs matching with DTO."""
        domain_document = self._convert_dto_to_domain(cv_document_dto)
        match_results = self.execute(domain_document)
        return [
            self._convert_to_match_result_dto(result)
            for result in match_results
        ]

    def _convert_dto_to_domain(self, dto: DocumentDto) -> Document:
        """Convert DTO to domain entity."""
        return Document(
            id=dto.id,
            document_type=DocumentType(dto.document_type),
            content=dto.content,
            metadata=dto.metadata,
        )

    def _convert_to_match_result_dto(
        self, match_result: MatchResult
    ) -> MatchResultDto:
        """Convert MatchResult to DTO."""
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
            detailed_results=match_result.detailed_results,
        )
