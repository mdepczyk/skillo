from abc import ABC, abstractmethod
from typing import Any, Dict, List

from skillo.domain.entities import Document, MatchResult
from skillo.domain.enums import DocumentType
from skillo.domain.factories import MatchResultFactory
from skillo.domain.repositories import DocumentRepository


class SupervisorAgentInterface(ABC):
    """Supervisor agent interface."""

    @abstractmethod
    def analyze_match(
        self, cv_document: Document, job_document: Document
    ) -> Dict[str, Any]:
        """Analyze CV-job match."""
        pass


class MatchingService:
    """CV-Job matching service."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        supervisor_agent: SupervisorAgentInterface,
        top_candidates_count: int = 5,
        min_match_score: float = 0.3,
    ):
        """Initialize with dependencies."""
        self._document_repository = document_repository
        self._supervisor_agent = supervisor_agent
        self._top_candidates_count = top_candidates_count
        self._min_match_score = min_match_score

    def match_cv_to_all_jobs(self, cv_document: Document) -> List[MatchResult]:
        """Match CV against all job postings."""
        return self._generic_match(
            source_document=cv_document,
            target_doc_type=DocumentType.JOB,
        )

    def match_job_to_all_cvs(
        self, job_document: Document
    ) -> List[MatchResult]:
        """Match job against all CVs."""
        return self._generic_match(
            source_document=job_document,
            target_doc_type=DocumentType.CV,
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

        matches = []
        for target_doc in target_documents:
            if len(matches) >= self._top_candidates_count:
                break

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

                match = MatchResultFactory.from_analysis_result(match_result)
                matches.append(match)

            except Exception:
                continue

        matches.sort(key=lambda x: x.weighted_final_score, reverse=True)

        filtered_matches = [
            match
            for match in matches
            if match.weighted_final_score >= self._min_match_score
        ]

        return filtered_matches[: self._top_candidates_count]


class ServiceContainer(ABC):
    """Service container interface."""

    @abstractmethod
    def upload_document(self):
        """Get upload document service."""
        pass

    @abstractmethod
    def get_document_list(self):
        """Get document list service."""
        pass

    @abstractmethod
    def get_document_stats(self):
        """Get document stats service."""
        pass

    @abstractmethod
    def match_cv_to_jobs(self):
        """Get match CV to jobs service."""
        pass

    @abstractmethod
    def match_job_to_cvs(self):
        """Get match job to CVs service."""
        pass

    @abstractmethod
    def reset_database(self):
        """Get reset database service."""
        pass

    @abstractmethod
    def export_to_csv(self):
        """Get export to CSV service."""
        pass

    @abstractmethod
    def logger(self):
        """Get logger."""
        pass

    @abstractmethod
    def config(self):
        """Get configuration."""
        pass

    @abstractmethod
    def document_processor(self):
        """Get document processor."""
        pass
