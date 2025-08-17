from typing import Any, Callable, List, Optional

from skillo.application.dto import DocumentDto, StatisticsDto
from skillo.application.mappers.dto_mapper import DTOMapper
from skillo.application.protocols import (
    DocumentProcessorProtocol,
    DocumentProtocol,
    ExportServiceProtocol,
    FileSystemProtocol,
    ListServiceProtocol,
    ResetServiceProtocol,
    StatsServiceProtocol,
    UploadServiceProtocol,
)
from skillo.application.use_cases.process_and_upload_documents import (
    BatchProcessResult,
    ProcessUploadedDocuments,
)
from skillo.domain.enums import DocumentType


class DocumentFacade(DocumentProtocol):
    """Document operations facade."""

    def __init__(
        self,
        upload_service: UploadServiceProtocol,
        stats_service: StatsServiceProtocol,
        list_service: ListServiceProtocol,
        reset_service: ResetServiceProtocol,
        export_service: ExportServiceProtocol,
        document_processor: DocumentProcessorProtocol,
        process_and_upload_service: ProcessUploadedDocuments,
        filesystem: FileSystemProtocol,
    ) -> None:
        """Initialize with services."""
        self._upload = upload_service
        self._stats = stats_service
        self._list = list_service
        self._reset = reset_service
        self._export = export_service
        self._processor = document_processor
        self._process_uploaded = process_and_upload_service
        self._filesystem = filesystem

    def upload_document(self, document_dto: DocumentDto) -> bool:
        """Uploads document."""
        return self._upload.execute_with_dto(document_dto)

    def get_statistics(self) -> StatisticsDto:
        """Document statistics."""
        return self._stats.execute_dto()

    def get_documents(
        self, document_type: Optional[str] = None
    ) -> List[DocumentDto]:
        """Document list."""
        return self._list.execute_dto(document_type)

    def reset_database(self) -> bool:
        """Resets database."""
        return self._reset.execute()

    def export_to_csv(self) -> str:
        """CSV export."""
        return self._export.execute()

    def process_document(self, file: Any, file_type: str) -> DocumentDto:
        """Processes document."""
        domain_document = self._processor.process_document(file, file_type)
        return DTOMapper.document_to_dto(domain_document)

    def process_uploaded_documents_parallel(
        self,
        files: List[Any],
        file_type: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> BatchProcessResult:
        """Process and upload multiple documents in parallel with progress tracking."""
        return self._process_uploaded.execute_with_progress(
            files, file_type, progress_callback
        )

    def get_file_path(
        self, filename: str, document_type: str
    ) -> Optional[str]:
        """File path."""
        doc_type = DocumentType(document_type)
        return self._list.get_file_path(filename, doc_type)

    def get_document_content(
        self, filename: str, document_type: str
    ) -> Optional[bytes]:
        """Document content."""
        file_path = self.get_file_path(filename, document_type)
        if file_path:
            return self._filesystem.read_file(file_path)
        return None
