from typing import Any, List, Optional

from skillo.application.dto import (
    ConfigDto,
    DocumentDto,
    DocumentTypeDto,
    LogEntryDto,
    LogLevelDto,
    MatchResultDto,
    StatisticsDto,
)
from skillo.domain.enums import DocumentType
from skillo.domain.services import ServiceContainer


class ApplicationFacade:
    """Application layer facade for UI."""

    def __init__(self, container: ServiceContainer) -> None:
        """Initialize with service container."""
        self._container = container

        self._upload_service = None
        self._get_stats_service = None
        self._get_document_list_service = None
        self._match_cv_to_jobs_service = None
        self._match_job_to_cvs_service = None
        self._reset_database_service = None
        self._export_to_csv_service = None
        self._logger = None

    def upload_document_dto(self, document_dto: DocumentDto) -> bool:
        """Upload document."""
        if self._upload_service is None:
            self._upload_service = self._container.upload_document()
        return self._upload_service.execute_with_dto(document_dto)

    def get_statistics(self) -> StatisticsDto:
        """Get document statistics."""
        if self._get_stats_service is None:
            self._get_stats_service = self._container.get_document_stats()
        return self._get_stats_service.execute_dto()

    def get_documents_dto(
        self, document_type: Optional[str] = None
    ) -> List[DocumentDto]:
        """Get list of documents, optionally filtered by type."""
        if self._get_document_list_service is None:
            self._get_document_list_service = (
                self._container.get_document_list()
            )
        return self._get_document_list_service.execute_dto(document_type)

    def reset_database(self) -> bool:
        """Reset the database."""
        if self._reset_database_service is None:
            self._reset_database_service = self._container.reset_database()
        return self._reset_database_service.execute()

    def export_to_csv(self) -> str:
        """Export documents to CSV."""
        if self._export_to_csv_service is None:
            self._export_to_csv_service = self._container.export_to_csv()
        return self._export_to_csv_service.execute()

    def get_config_values(self) -> ConfigDto:
        """Get configuration values."""
        config = self._container.config()
        return ConfigDto(
            chroma_db_path=config.CHROMA_DB_PATH,
            collection_name=config.COLLECTION_NAME,
            embedding_model=config.EMBEDDING_MODEL,
            min_match_score=config.MIN_MATCH_SCORE,
            top_candidates_count=config.TOP_CANDIDATES_COUNT,
            agent_weights=config.AGENT_WEIGHTS,
        )

    def process_document(self, file: Any, file_type: str) -> DocumentDto:
        """Process document."""
        processor = self._container.document_processor()
        return processor.process_document_dto(file, file_type)

    def get_log_levels_dto(self) -> type:
        """Get LogLevel constants."""
        return LogLevelDto

    def get_document_types_dto(self) -> type:
        """Get DocumentType constants."""
        return DocumentTypeDto

    def match_cv_to_jobs_dto(
        self, cv_document_dto: DocumentDto
    ) -> List[MatchResultDto]:
        """Find job matches for CV."""
        if self._match_cv_to_jobs_service is None:
            self._match_cv_to_jobs_service = self._container.match_cv_to_jobs()
        return self._match_cv_to_jobs_service.execute_dto(cv_document_dto)

    def match_job_to_cvs_dto(
        self, job_document_dto: DocumentDto
    ) -> List[MatchResultDto]:
        """Find CV matches for job."""
        if self._match_job_to_cvs_service is None:
            self._match_job_to_cvs_service = self._container.match_job_to_cvs()
        return self._match_job_to_cvs_service.execute_dto(job_document_dto)

    def get_logs(self, last_n: Optional[int] = None) -> List[LogEntryDto]:
        """Get logs."""
        if self._logger is None:
            self._logger = self._container.logger()
        return self._logger.get_logs_dto(last_n)

    def clear_logs(self) -> None:
        """Clear logs."""
        if self._logger is None:
            self._logger = self._container.logger()
        self._logger.clear_logs()

    def get_file_path(
        self, filename: str, document_type: str
    ) -> Optional[str]:
        """Get file path."""
        if self._get_document_list_service is None:
            self._get_document_list_service = (
                self._container.get_document_list()
            )

        doc_type = DocumentType(document_type)
        return self._get_document_list_service.get_file_path(
            filename, doc_type
        )

    def get_document_content_dto(
        self, filename: str, document_type: str
    ) -> Optional[bytes]:
        """Get document content."""
        file_path = self.get_file_path(filename, document_type)
        if file_path:
            import os

            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        return f.read()
                except Exception:
                    return None
        return None
