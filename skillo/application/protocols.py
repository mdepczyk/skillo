from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Protocol

if TYPE_CHECKING:
    from skillo.domain.entities import Document
    from skillo.application.use_cases.process_and_upload_documents import (
        BatchProcessResult,
    )

from skillo.application.dto import (
    ConfigDto,
    DocumentDto,
    EventDto,
    LogEntryDto,
    MatchResultDto,
    StatisticsDto,
)


class DocumentProtocol(Protocol):
    """Document operations protocol."""

    def upload_document(self, document_dto: DocumentDto) -> bool:
        """Upload document."""
        ...

    def get_statistics(self) -> StatisticsDto:
        """Get document statistics."""
        ...

    def get_documents(
        self, document_type: Optional[str] = None
    ) -> List[DocumentDto]:
        """Get list of documents, optionally filtered by type."""
        ...

    def reset_database(self) -> bool:
        """Reset the database."""
        ...

    def export_to_csv(self) -> str:
        """Export documents to CSV."""
        ...

    def process_document(self, file: bytes, file_type: str) -> DocumentDto:
        """Process document."""
        ...

    def get_file_path(
        self, filename: str, document_type: str
    ) -> Optional[str]:
        """Get file path."""
        ...

    def get_document_content(
        self, filename: str, document_type: str
    ) -> Optional[bytes]:
        """Get document content."""
        ...

    def process_uploaded_documents_parallel(
        self,
        files: List[object],
        file_type: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> "BatchProcessResult":
        """Process and upload multiple documents in parallel with progress tracking."""
        ...


class MatchingProtocol(Protocol):
    """Matching operations protocol."""

    def match_cv_to_jobs(
        self, cv_document_dto: DocumentDto
    ) -> List[MatchResultDto]:
        """Find job matches for CV."""
        ...

    def match_job_to_cvs(
        self, job_document_dto: DocumentDto
    ) -> List[MatchResultDto]:
        """Find CV matches for job."""
        ...

    def match_cv_to_jobs_with_progress(
        self,
        cv_document_dto: DocumentDto,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResultDto]:
        """Find job matches for CV with progress tracking."""
        ...

    def match_job_to_cvs_with_progress(
        self,
        job_document_dto: DocumentDto,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResultDto]:
        """Find CV matches for job with progress tracking."""
        ...


class ConfigProtocol(Protocol):
    """Configuration operations protocol."""

    def get_config_values(self) -> ConfigDto:
        """Get configuration values."""
        ...

    def get_logs(self, last_n: Optional[int] = None) -> List[LogEntryDto]:
        """Get logs."""
        ...

    def clear_logs(self) -> None:
        """Clear logs."""
        ...


class ApplicationFacadeProtocol(Protocol):
    """Application facade protocol."""

    @property
    def documents(self) -> DocumentProtocol:
        """Get document facade."""
        ...

    @property
    def matching(self) -> MatchingProtocol:
        """Get matching facade."""
        ...

    @property
    def config(self) -> ConfigProtocol:
        """Get configuration facade."""
        ...


class NotificationService(Protocol):
    """Notification service protocol."""

    def show_success(self, message: str) -> None:
        """Success notification."""
        ...

    def show_error(self, message: str) -> None:
        """Error notification."""
        ...

    def show_info(self, message: str) -> None:
        """Info notification."""
        ...

    def show_warning(self, message: str) -> None:
        """Warning notification."""
        ...


class EventHandler(Protocol):
    """Event handler protocol."""

    def handle(self, event: EventDto) -> None:
        """Event handler."""
        ...


class UploadServiceProtocol(Protocol):
    """Upload service protocol."""

    def execute(self, document: "Document") -> bool:
        """Execute upload with Domain entity."""
        ...

    def execute_with_dto(self, document_dto: DocumentDto) -> bool:
        """Execute upload with DTO."""
        ...


class StatsServiceProtocol(Protocol):
    """Statistics service protocol."""

    def execute_dto(self) -> StatisticsDto:
        """Execute stats."""
        ...


class ListServiceProtocol(Protocol):
    """List service protocol."""

    def execute_dto(self, document_type: Optional[str]) -> List[DocumentDto]:
        """Execute list."""
        ...

    def get_file_path(self, filename: str, doc_type: str) -> Optional[str]:
        """Get file path."""
        ...


class ResetServiceProtocol(Protocol):
    """Reset service protocol."""

    def execute(self) -> bool:
        """Execute reset."""
        ...


class ExportServiceProtocol(Protocol):
    """Export service protocol."""

    def execute(self) -> str:
        """Execute export."""
        ...


class DocumentProcessorProtocol(Protocol):
    """Document processor protocol."""

    def process_document(self, file: bytes, file_type: str) -> "Document":
        """Process document."""
        ...


class MatchingServiceProtocol(Protocol):
    """Matching service protocol."""

    def execute_dto(self, document_dto: DocumentDto) -> List[MatchResultDto]:
        """Execute matching."""
        ...

    def execute_dto_with_progress(
        self,
        document_dto: DocumentDto,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[MatchResultDto]:
        """Execute matching with progress tracking."""
        ...


class ConfigServiceProtocol(Protocol):
    """Config service protocol."""

    CHROMA_DB_PATH: str
    COLLECTION_NAME: str
    EMBEDDING_MODEL: str
    MIN_MATCH_SCORE: float
    TOP_CANDIDATES_COUNT: int
    AGENT_WEIGHTS: Dict[str, float]


class LoggerServiceProtocol(Protocol):
    """Logger service protocol."""

    def get_logs(self, last_n: Optional[int]) -> List[LogEntryDto]:
        """Get logs."""
        ...

    def clear_logs(self) -> None:
        """Clear logs."""
        ...


class FileSystemProtocol(Protocol):
    """File system operations protocol."""

    def read_file(self, file_path: str) -> Optional[bytes]:
        """Read file content as bytes."""
        ...

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        ...

    def join_path(self, *parts: str) -> str:
        """Join path components."""
        ...
