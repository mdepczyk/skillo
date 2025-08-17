from skillo.application.dto import DocumentDto
from skillo.domain.entities import Document
from skillo.domain.exceptions import SkilloProcessingError
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.processing.cv_processor import CVDocumentProcessor
from skillo.infrastructure.processing.job_processor import JobDocumentProcessor


class DocumentProcessor:
    """Main document processor that delegates to specialized processors."""

    def __init__(self, config: Config, cv_agent, job_agent, normalizer):
        self.config = config
        self._cv_processor = CVDocumentProcessor(config, cv_agent, normalizer)
        self._job_processor = JobDocumentProcessor(config, job_agent, normalizer)

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF."""
        return self._cv_processor.extract_text_from_pdf(pdf_file)

    def generate_document_id(self, content: str, filename: str) -> str:
        """Generate document ID."""
        return self._cv_processor.generate_document_id(content, filename)

    def save_uploaded_file(self, uploaded_file, file_type: str) -> str:
        """Save uploaded file and return path."""
        if file_type == "cv":
            save_dir = self.config.CV_UPLOAD_DIR
        elif file_type == "job":
            save_dir = self.config.JOB_UPLOAD_DIR
        else:
            raise SkilloProcessingError(
                f"Invalid file type '{file_type}', only PDF files are supported"
            )

        return self._cv_processor.save_uploaded_file(uploaded_file, save_dir)

    def process_document(self, uploaded_file, file_type: str) -> Document:
        """Process PDF document with appropriate processor."""
        text_content = self.extract_text_from_pdf(uploaded_file)

        if not text_content:
            raise SkilloProcessingError(
                f"Empty document '{uploaded_file.name}' - no text could be extracted"
            )

        doc_id = self.generate_document_id(text_content, uploaded_file.name)

        try:
            if file_type == "cv":
                return self._cv_processor.process_document_content(
                    text_content, uploaded_file.name, doc_id
                )
            elif file_type == "job":
                return self._job_processor.process_document_content(
                    text_content, uploaded_file.name, doc_id
                )
            else:
                raise SkilloProcessingError(
                    f"Invalid file type '{file_type}' in batch processing"
                )

        except Exception as e:
            raise SkilloProcessingError(
                f"Processing '{uploaded_file.name}' failed: {str(e)}"
            )

    def process_document_dto(
        self, uploaded_file, file_type: str
    ) -> DocumentDto:
        """Process document and return DTO."""
        domain_document = self.process_document(uploaded_file, file_type)
        return DocumentDto(
            id=domain_document.id,
            document_type=domain_document.document_type.value,
            content=domain_document.content,
            metadata=domain_document.metadata,
        )