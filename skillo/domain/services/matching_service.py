from typing import Callable, List, Optional

from skillo.domain.entities import Document, MatchResult
from skillo.domain.enums import DocumentType
from skillo.domain.exceptions import SkilloAnalysisError
from skillo.domain.factories import MatchResultFactory
from skillo.domain.repositories import DocumentRepository

from .interfaces import ParallelExecutionService, SupervisorAgentInterface


class MatchingService:
    """CV-Job matching service."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        supervisor_agent: SupervisorAgentInterface,
        parallel_executor: ParallelExecutionService,
        top_candidates_count: int = 5,
        min_match_score: float = 0.3,
    ):
        """Initialize with dependencies."""
        self._document_repository = document_repository
        self._supervisor_agent = supervisor_agent
        self._parallel_executor = parallel_executor
        self._top_candidates_count = top_candidates_count
        self._min_match_score = min_match_score

    def match_cv_to_all_jobs(self, cv_document: Document) -> List[MatchResult]:
        """Match CV against all job postings."""
        return self._generic_match(
            source_document=cv_document,
            target_doc_type=DocumentType.JOB,
        )

    def match_cv_to_all_jobs_with_progress(
        self,
        cv_document: Document,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResult]:
        """Match CV against all job postings with progress tracking."""
        return self._generic_match_with_progress(
            source_document=cv_document,
            target_doc_type=DocumentType.JOB,
            progress_callback=progress_callback,
        )

    def match_job_to_all_cvs(
        self, job_document: Document
    ) -> List[MatchResult]:
        """Match job against all CVs."""
        return self._generic_match(
            source_document=job_document,
            target_doc_type=DocumentType.CV,
        )

    def match_job_to_all_cvs_with_progress(
        self,
        job_document: Document,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResult]:
        """Match job against all CVs with progress tracking."""
        return self._generic_match_with_progress(
            source_document=job_document,
            target_doc_type=DocumentType.CV,
            progress_callback=progress_callback,
        )

    def _generic_match(
        self,
        source_document: Document,
        target_doc_type: DocumentType,
    ) -> List[MatchResult]:
        """Generic matching method."""
        target_documents = self._document_repository.find_similar_documents(
            query=source_document.content,
            doc_type=target_doc_type,
            limit=self._top_candidates_count * 2,
        )

        if not target_documents:
            return []

        tasks = [
            lambda td=target_doc: self._analyze_single_match(
                source_document, td, target_doc_type
            )
            for target_doc in target_documents
        ]

        matches = self._parallel_executor.execute_tasks_with_progress(tasks)

        matches.sort(key=lambda x: x.weighted_final_score, reverse=True)

        filtered_matches = [
            match
            for match in matches
            if match.weighted_final_score >= self._min_match_score
        ]

        return filtered_matches[: self._top_candidates_count]

    def _generic_match_with_progress(
        self,
        source_document: Document,
        target_doc_type: DocumentType,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResult]:
        """Generic matching method with progress tracking."""
        target_documents = self._document_repository.find_similar_documents(
            query=source_document.content,
            doc_type=target_doc_type,
            limit=self._top_candidates_count * 2,
        )

        if not target_documents:
            return []

        tasks = [
            lambda td=target_doc: self._analyze_single_match(
                source_document, td, target_doc_type
            )
            for target_doc in target_documents
        ]

        matches = self._parallel_executor.execute_tasks_with_progress(
            tasks, progress_callback
        )

        matches.sort(key=lambda x: x.weighted_final_score, reverse=True)

        filtered_matches = [
            match
            for match in matches
            if match.weighted_final_score >= self._min_match_score
        ]

        return filtered_matches[: self._top_candidates_count]

    def _analyze_single_match(
        self,
        source_document: Document,
        target_doc: Document,
        target_doc_type: DocumentType,
    ) -> MatchResult | None:
        """Analyze single document match - thread-safe."""
        try:
            if target_doc_type == DocumentType.JOB:
                match_result = self._supervisor_agent.analyze_match(
                    cv_document=source_document, job_document=target_doc
                )
                match_result["cv_document"] = source_document
                match_result["job_document"] = target_doc
            else:
                match_result = self._supervisor_agent.analyze_match(
                    cv_document=target_doc, job_document=source_document
                )
                match_result["cv_document"] = target_doc
                match_result["job_document"] = source_document

            return MatchResultFactory.from_analysis_result(match_result)

        except (SkilloAnalysisError, ValueError):
            return None
        except Exception:
            return None
