from .base import BaseEvent


class DatabaseResetEvent(BaseEvent):
    """Database reset event."""

    def __init__(self, success: bool, error_message: str = ""):
        super().__init__()
        self.success = success
        self.error_message = error_message

    @property
    def event_type(self) -> str:
        return "DATABASE_RESET"

    @property
    def message(self) -> str:
        if self.success:
            return "Database reset completed successfully"
        return f"Database reset failed: {self.error_message}"

    @property
    def level(self) -> str:
        return "success" if self.success else "error"


class DocumentExportCompletedEvent(BaseEvent):
    """Document export completed event."""

    def __init__(self, document_count: int, export_format: str):
        super().__init__()
        self.document_count = document_count
        self.export_format = export_format

    @property
    def event_type(self) -> str:
        return "DOCUMENT_EXPORT_COMPLETED"

    @property
    def message(self) -> str:
        return f"Exported {self.document_count} documents to {self.export_format.upper()}"

    @property
    def level(self) -> str:
        return "success"


class DocumentExportFailedEvent(BaseEvent):
    """Document export failed event."""

    def __init__(self, error_message: str, export_format: str):
        super().__init__()
        self.error_message = error_message
        self.export_format = export_format

    @property
    def event_type(self) -> str:
        return "DOCUMENT_EXPORT_FAILED"

    @property
    def message(self) -> str:
        return f"Failed to export to {self.export_format.upper()}: {self.error_message}"

    @property
    def level(self) -> str:
        return "error"
