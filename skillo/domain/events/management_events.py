from dataclasses import dataclass


@dataclass
class DatabaseResetEvent:
    """Database reset event."""

    success: bool
    error_message: str = ""

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


@dataclass
class DocumentExportCompletedEvent:
    """Document export completed event."""

    document_count: int
    export_format: str

    @property
    def event_type(self) -> str:
        return "DOCUMENT_EXPORT_COMPLETED"

    @property
    def message(self) -> str:
        return f"Exported {self.document_count} documents to {self.export_format.upper()}"

    @property
    def level(self) -> str:
        return "success"


@dataclass
class DocumentExportFailedEvent:
    """Document export failed event."""

    error_message: str
    export_format: str

    @property
    def event_type(self) -> str:
        return "DOCUMENT_EXPORT_FAILED"

    @property
    def message(self) -> str:
        return f"Failed to export to {self.export_format.upper()}: {self.error_message}"

    @property
    def level(self) -> str:
        return "error"
