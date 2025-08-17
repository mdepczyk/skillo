from typing import Callable, List, Optional

from skillo.application.dto import DocumentDto, MatchResultDto
from skillo.application.mappers import DTOMapper
from skillo.domain.entities import Document, MatchResult
from skillo.domain.events import (
    EventPublisher,
    MatchingCompletedEvent,
    MatchingFailedEvent,
)
from skillo.domain.events.base import BaseEvent
from skillo.domain.repositories import DocumentRepository
from skillo.domain.services import (
    MatchingService,
    SupervisorAgentInterface,
)
from skillo.domain.services.interfaces import ParallelExecutionService


class MatchCVToJobs:
    """Match CV against available jobs."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        supervisor_agent: SupervisorAgentInterface,
        parallel_executor: ParallelExecutionService,
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
            parallel_executor=parallel_executor,
            top_candidates_count=top_candidates_count,
            min_match_score=min_match_score,
        )

    def execute(self, cv_document: Document) -> List[MatchResult]:
        """Execute CV to jobs matching workflow."""
        try:
            matches = self._matching_service.match_cv_to_all_jobs(cv_document)

            if matches:
                event = MatchingCompletedEvent(
                    message=f"Found {len(matches)} job matches",
                    context="CV to Jobs Matching",
                )
            else:
                event = MatchingCompletedEvent(
                    message="No job matches found",
                    context="CV to Jobs Matching",
                )

            self._event_publisher.publish(event)

            return matches

        except Exception as e:
            from skillo.domain.exceptions import SkilloMatchingError

            error_msg = f"CV matching workflow failed: {str(e)}"
            error_event: BaseEvent = MatchingFailedEvent(
                error_message=error_msg,
                context="CV to Jobs Matching",
            )
            self._event_publisher.publish(error_event)
            raise SkilloMatchingError(error_msg)

    def execute_dto(
        self, cv_document_dto: DocumentDto
    ) -> List[MatchResultDto]:
        """Execute CV to jobs matching with DTO."""
        domain_document = DTOMapper.dto_to_document(cv_document_dto)
        match_results = self.execute(domain_document)
        return DTOMapper.match_results_to_dtos(match_results)

    def execute_with_progress(
        self,
        cv_document: Document,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResult]:
        """Execute CV to jobs matching with progress tracking."""
        try:
            matches = (
                self._matching_service.match_cv_to_all_jobs_with_progress(
                    cv_document, progress_callback
                )
            )

            if matches:
                event = MatchingCompletedEvent(
                    message=f"Found {len(matches)} job matches",
                    context="CV to Jobs Matching",
                )
            else:
                event = MatchingCompletedEvent(
                    message="No job matches found",
                    context="CV to Jobs Matching",
                )

            self._event_publisher.publish(event)

            return matches

        except Exception as e:
            from skillo.domain.exceptions import SkilloMatchingError

            error_msg = f"CV matching workflow failed: {str(e)}"
            error_event: BaseEvent = MatchingFailedEvent(
                error_message=error_msg,
                context="CV to Jobs Matching",
            )
            self._event_publisher.publish(error_event)
            raise SkilloMatchingError(error_msg)

    def execute_dto_with_progress(
        self,
        cv_document_dto: DocumentDto,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResultDto]:
        """Execute CV to jobs matching with DTO and progress tracking."""
        domain_document = DTOMapper.dto_to_document(cv_document_dto)
        match_results = self.execute_with_progress(
            domain_document, progress_callback
        )
        return DTOMapper.match_results_to_dtos(match_results)
