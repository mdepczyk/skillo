from skillo.domain.events import (
    DocumentExportCompletedEvent,
    DocumentExportFailedEvent,
    EventPublisher,
)
from skillo.domain.events.base import BaseEvent
from skillo.domain.repositories import ManagementRepository


class ExportToCSV:
    """Export documents to CSV."""

    def __init__(
        self,
        management_repository: ManagementRepository,
        event_publisher: EventPublisher,
    ):
        """Initialize with dependencies."""
        self._management_repository = management_repository
        self._event_publisher = event_publisher

    def execute(self) -> str:
        """Execute CSV export workflow."""
        try:
            documents = self._management_repository.get_all_documents()

            if not documents:
                csv_content = "id,document_type,content,metadata\n"

                event: BaseEvent = DocumentExportCompletedEvent(
                    document_count=0, export_format="CSV"
                )
                self._event_publisher.publish(event)

                return csv_content

            csv_lines = ["id,document_type,content,metadata"]

            for doc in documents:
                content = doc.content.replace('"', '""')
                metadata = str(doc.metadata).replace('"', '""')

                csv_lines.append(
                    f'"{doc.id}","{doc.document_type.value}","{content}","{metadata}"'
                )

            csv_content = "\n".join(csv_lines)

            success_event: BaseEvent = DocumentExportCompletedEvent(
                document_count=len(documents), export_format="CSV"
            )
            self._event_publisher.publish(success_event)

            return csv_content

        except Exception as e:
            error_event: BaseEvent = DocumentExportFailedEvent(
                error_message=str(e), export_format="CSV"
            )
            self._event_publisher.publish(error_event)
            raise e
