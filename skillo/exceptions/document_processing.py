"""Document processing related exceptions."""


class PDFExtractionError(Exception):
    """Failed to extract text content from PDF file."""

    def __init__(self, filename: str = "", original_error: str = ""):
        message = (
            f"Cannot extract text from PDF file '{filename}': {original_error}"
        )
        super().__init__(message)


class FileUploadError(Exception):
    """Failed to save uploaded file to storage directory."""

    def __init__(
        self, filename: str = "", file_type: str = "", original_error: str = ""
    ):
        message = f"Cannot save {file_type} file '{filename}' to storage: {original_error}"
        super().__init__(message)


class DocumentProcessingError(Exception):
    """Document processing with specialized agents failed."""

    def __init__(
        self, file_type: str = "", filename: str = "", original_error: str = ""
    ):
        message = f"Processing {file_type} document '{filename}' failed: {original_error}"
        super().__init__(message)


class InvalidFileTypeError(Exception):
    """Unsupported file type provided for processing."""

    def __init__(self, file_type: str = ""):
        message = f"File type '{file_type}' is not supported. Only 'cv' and 'job' types are allowed"
        super().__init__(message)


class EmptyDocumentError(Exception):
    """Document contains no extractable text content."""

    def __init__(self, filename: str = ""):
        message = f"Document '{filename}' contains no extractable text content"
        super().__init__(message)
