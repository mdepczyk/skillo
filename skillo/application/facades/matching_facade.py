from typing import Callable, List, Optional

from skillo.application.dto import DocumentDto, MatchResultDto
from skillo.application.protocols import (
    MatchingProtocol,
    MatchingServiceProtocol,
)


class MatchingFacade(MatchingProtocol):
    """CV-job matching facade."""

    def __init__(
        self,
        cv_to_jobs_service: MatchingServiceProtocol,
        job_to_cvs_service: MatchingServiceProtocol,
    ) -> None:
        """Initialize with services."""
        self._cv_to_jobs = cv_to_jobs_service
        self._job_to_cvs = job_to_cvs_service

    def match_cv_to_jobs(
        self, cv_document_dto: DocumentDto
    ) -> List[MatchResultDto]:
        """Job matches for CV."""
        return self._cv_to_jobs.execute_dto(cv_document_dto)

    def match_cv_to_jobs_with_progress(
        self,
        cv_document_dto: DocumentDto,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResultDto]:
        """Job matches for CV with progress tracking."""
        return self._cv_to_jobs.execute_dto_with_progress(
            cv_document_dto, progress_callback
        )

    def match_job_to_cvs(
        self, job_document_dto: DocumentDto
    ) -> List[MatchResultDto]:
        """CV matches for job."""
        return self._job_to_cvs.execute_dto(job_document_dto)

    def match_job_to_cvs_with_progress(
        self,
        job_document_dto: DocumentDto,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResultDto]:
        """CV matches for job with progress tracking."""
        return self._job_to_cvs.execute_dto_with_progress(
            job_document_dto, progress_callback
        )
