from dataclasses import dataclass


@dataclass
class DocumentUploadedEvent:
    """Document uploaded event."""

    filename: str
    document_type: str

    @property
    def event_type(self) -> str:
        return "DOCUMENT_UPLOADED"

    @property
    def message(self) -> str:
        return f"{self.document_type} '{self.filename}' uploaded successfully"

    @property
    def level(self) -> str:
        return "success"


@dataclass
class DocumentUploadFailedEvent:
    """Document upload failed event."""

    filename: str
    document_type: str
    error_message: str

    @property
    def event_type(self) -> str:
        return "DOCUMENT_UPLOAD_FAILED"

    @property
    def message(self) -> str:
        return f"Failed to upload {self.document_type} '{self.filename}': {self.error_message}"

    @property
    def level(self) -> str:
        return "error"
