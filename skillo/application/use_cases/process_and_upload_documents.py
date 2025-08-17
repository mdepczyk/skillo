from typing import Any, Callable, Dict, List, Optional

from skillo.application.protocols import (
    DocumentProcessorProtocol,
    UploadServiceProtocol,
)
from skillo.domain.events import EventPublisher
from skillo.domain.services.interfaces import ParallelExecutionService


class BatchProcessResult:
    """Result of batch document processing and upload operation."""

    def __init__(self) -> None:
        self.successful_uploads = 0
        self.failed_uploads = 0
        self.results: List[Dict[str, Any]] = []

    def add_success(self, filename: str) -> None:
        """Add successful processing result."""
        self.successful_uploads += 1
        self.results.append(
            {"filename": filename, "success": True, "error": None}
        )

    def add_failure(self, filename: str, error: str) -> None:
        """Add failed processing result."""
        self.failed_uploads += 1
        self.results.append(
            {"filename": filename, "success": False, "error": error}
        )


class ProcessUploadedDocuments:
    """Process and upload documents in parallel - combines processing + upload workflow."""

    def __init__(
        self,
        document_processor: DocumentProcessorProtocol,
        upload_service: UploadServiceProtocol,
        parallel_executor: ParallelExecutionService,
        event_publisher: EventPublisher,
    ):
        """Initialize with Clean Architecture dependencies."""
        self._document_processor = document_processor
        self._upload_service = upload_service
        self._parallel_executor = parallel_executor
        self._event_publisher = event_publisher

    def execute_with_progress(
        self,
        files: List[Any],
        file_type: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> BatchProcessResult:
        """Execute complete parallel processing and upload workflow."""
        if not files:
            return BatchProcessResult()

        tasks = [
            lambda f=file: self._process_uploaded_single_file(f, file_type)
            for file in files
        ]

        results = self._parallel_executor.execute_tasks_with_progress(
            tasks, progress_callback
        )

        batch_result = BatchProcessResult()
        for result in results:
            if result and result.get("success"):
                batch_result.add_success(result["filename"])
            else:
                error_msg = (
                    result.get("error", "Unknown error")
                    if result
                    else "Task failed"
                )
                filename = (
                    result.get("filename", "Unknown") if result else "Unknown"
                )
                batch_result.add_failure(filename, error_msg)

        return batch_result

    def _process_uploaded_single_file(
        self, file: Any, file_type: str
    ) -> Dict[str, Any]:
        """Process and upload single file - designed for parallel execution."""
        filename = getattr(file, "name", "Unknown")

        try:
            domain_document = self._document_processor.process_document(
                file, file_type
            )

            if not domain_document:
                return {
                    "filename": filename,
                    "success": False,
                    "error": "Document processing failed",
                }

            success = self._upload_service.execute(domain_document)

            if success:
                return {"filename": filename, "success": True, "error": None}
            else:
                return {
                    "filename": filename,
                    "success": False,
                    "error": "Database upload failed",
                }

        except Exception as e:
            return {
                "filename": filename,
                "success": False,
                "error": f"Processing error: {str(e)}",
            }
