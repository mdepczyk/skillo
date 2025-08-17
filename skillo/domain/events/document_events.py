from .base import BaseEvent


class DocumentUploadedEvent(BaseEvent):
    """Document uploaded event."""

    def __init__(self, filename: str, document_type: str):
        super().__init__()
        self.filename = filename
        self.document_type = document_type

    @property
    def event_type(self) -> str:
        return "DOCUMENT_UPLOADED"

    @property
    def message(self) -> str:
        return f"{self.document_type} '{self.filename}' uploaded successfully"

    @property
    def level(self) -> str:
        return "success"


class DocumentUploadFailedEvent(BaseEvent):
    """Document upload failed event."""

    def __init__(self, filename: str, document_type: str, error_message: str):
        super().__init__()
        self.filename = filename
        self.document_type = document_type
        self.error_message = error_message

    @property
    def event_type(self) -> str:
        return "DOCUMENT_UPLOAD_FAILED"

    @property
    def message(self) -> str:
        return f"Failed to upload {self.document_type} '{self.filename}': {self.error_message}"

    @property
    def level(self) -> str:
        return "error"
