from skillo.application.dto import DocumentDto
from skillo.application.mappers import DTOMapper
from skillo.domain.entities import Document
from skillo.domain.events import (
    DocumentUploadedEvent,
    DocumentUploadFailedEvent,
    EventPublisher,
)
from skillo.domain.events.base import BaseEvent
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
            document_type = document.document_type.value.upper()
            success = self._document_repository.add_document(document)

            event: BaseEvent
            if success:
                event = DocumentUploadedEvent(
                    filename=document.metadata.get("filename", "Unknown"),
                    document_type=document_type,
                )
            else:
                event = DocumentUploadFailedEvent(
                    filename=document.metadata.get("filename", "Unknown"),
                    document_type=document_type,
                    error_message="Failed to add document to repository",
                )
            self._event_publisher.publish(event)

            return success

        except Exception as e:
            from skillo.domain.exceptions import SkilloRepositoryError

            document_type = document.document_type.value.upper()
            error_msg = f"{document_type} upload workflow failed: {str(e)}"
            event = DocumentUploadFailedEvent(
                filename=document.metadata.get("filename", "Unknown"),
                document_type=document_type,
                error_message=error_msg,
            )
            self._event_publisher.publish(event)
            raise SkilloRepositoryError(error_msg)

    def execute_with_dto(self, document_dto: DocumentDto) -> bool:
        """Execute document upload with DTO input."""
        domain_document = DTOMapper.dto_to_document(document_dto)
        return self.execute(domain_document)
