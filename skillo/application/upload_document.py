from skillo.application.dto import DocumentDto
from skillo.domain.entities import Document
from skillo.domain.enums import DocumentType
from skillo.domain.events import (
    DocumentUploadedEvent,
    DocumentUploadFailedEvent,
    EventPublisher,
)
from skillo.domain.repositories import DocumentRepository


class UploadDocument:
    """Upload and process documents."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        event_publisher: EventPublisher,
    ):
        """Initialize with dependencies."""
        self._document_repository = document_repository
        self._event_publisher = event_publisher

    def execute(self, document: Document) -> bool:
        """Execute document upload workflow."""
        try:
            document_type = (
                "CV" if document.document_type == DocumentType.CV else "Job"
            )
            success = self._document_repository.add_document(document)

            if success:
                event = DocumentUploadedEvent(
                    filename=document.metadata.get("filename", "Unknown"),
                    document_type=document_type,
                )
                self._event_publisher.publish(event)
            else:
                event = DocumentUploadFailedEvent(
                    filename=document.metadata.get("filename", "Unknown"),
                    document_type=document_type,
                    error_message="Failed to add document to repository",
                )
                self._event_publisher.publish(event)

            return success

        except Exception as e:
            document_type = (
                "CV" if document.document_type == DocumentType.CV else "Job"
            )
            error_msg = f"{document_type} upload workflow failed: {str(e)}"
            event = DocumentUploadFailedEvent(
                filename=document.metadata.get("filename", "Unknown"),
                document_type=document_type,
                error_message=error_msg,
            )
            self._event_publisher.publish(event)
            return False

    def execute_with_dto(self, document_dto: DocumentDto) -> bool:
        """Execute document upload with DTO input."""
        domain_document = self._convert_dto_to_domain(document_dto)
        return self.execute(domain_document)

    def _convert_dto_to_domain(self, dto: DocumentDto) -> Document:
        """Convert DTO to domain entity."""
        return Document(
            id=dto.id,
            document_type=DocumentType(dto.document_type),
            content=dto.content,
            metadata=dto.metadata,
        )
