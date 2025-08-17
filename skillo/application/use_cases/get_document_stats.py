from typing import Any, Dict

from skillo.application.dto import StatisticsDto
from skillo.application.mappers import DTOMapper
from skillo.domain.enums import DocumentType
from skillo.domain.repositories import DocumentRepository


class GetDocumentStats:
    """Get document statistics."""

    def __init__(self, document_repository: DocumentRepository):
        """Initialize with dependencies."""
        self._document_repository = document_repository

    def execute(self) -> Dict[str, Any]:
        """Execute get document stats workflow."""
        try:
            cv_documents = self._document_repository.get_documents_by_type(
                DocumentType.CV
            )
            job_documents = self._document_repository.get_documents_by_type(
                DocumentType.JOB
            )

            stats = {
                "total_documents": len(cv_documents) + len(job_documents),
                "cv_count": len(cv_documents),
                "job_count": len(job_documents),
                "cv_documents": cv_documents,
                "job_documents": job_documents,
            }

            return stats

        except Exception as e:
            from skillo.domain.exceptions import SkilloRepositoryError

            raise SkilloRepositoryError(
                f"Failed to retrieve document statistics: {str(e)}"
            )

    def execute_dto(self) -> StatisticsDto:
        """Get document stats as DTO."""
        raw_stats = self.execute()
        return StatisticsDto(
            total_documents=raw_stats["total_documents"],
            cv_count=raw_stats["cv_count"],
            job_count=raw_stats["job_count"],
            cv_documents=DTOMapper.documents_to_dtos(
                raw_stats["cv_documents"]
            ),
            job_documents=DTOMapper.documents_to_dtos(
                raw_stats["job_documents"]
            ),
        )
