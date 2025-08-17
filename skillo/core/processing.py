import hashlib
import os
from typing import Any, Dict

from pypdf import PdfReader

from skillo.config import Config
from skillo.exceptions import (
    DocumentProcessingError,
    EmptyDocumentError,
    InvalidFileTypeError,
    PDFExtractionError,
)


class DocumentProcessor:
    """Handle PDF document processing and text extraction"""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text content from PDF file"""
        try:
            reader = PdfReader(pdf_file)

            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            raise PDFExtractionError(
                getattr(pdf_file, "name", "unknown"), str(e)
            )

    def generate_document_id(self, content: str, filename: str) -> str:
        """Generate unique ID for document based on content and filename"""
        combined = f"{filename}_{content[:100]}"
        return hashlib.md5(combined.encode()).hexdigest()

    def save_uploaded_file(self, uploaded_file, file_type: str) -> str:
        """Save uploaded file to appropriate directory and return file path"""
        if file_type == "cv":
            save_dir = self.config.CV_UPLOAD_DIR
        elif file_type == "job":
            save_dir = self.config.JOB_UPLOAD_DIR
        else:
            raise InvalidFileTypeError(file_type)

        os.makedirs(save_dir, exist_ok=True)

        file_path = os.path.join(save_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path

    def process_document(
        self, uploaded_file, file_type: str
    ) -> Dict[str, Any]:
        """Process uploaded PDF document with Document Processing and Normalization agents"""
        from skillo.core.matcher import JobMatcher

        text_content = self.extract_text_from_pdf(uploaded_file)

        if not text_content:
            raise EmptyDocumentError(uploaded_file.name)

        doc_id = self.generate_document_id(text_content, uploaded_file.name)

        file_path = self.save_uploaded_file(uploaded_file, file_type)

        metadata = {
            "filename": uploaded_file.name,
            "file_path": file_path,
            "file_size": len(uploaded_file.getvalue()),
            "char_count": len(text_content),
            "word_count": len(text_content.split()),
        }

        matcher = JobMatcher(self.config)

        try:
            if file_type == "cv":
                processed_document = matcher.process_cv_document(
                    text_content, metadata
                )
            elif file_type == "job":
                processed_document = matcher.process_job_document(
                    text_content, metadata
                )
            else:
                raise InvalidFileTypeError(file_type)

            processed_document["id"] = doc_id

            return processed_document

        except Exception as e:
            raise DocumentProcessingError(
                file_type, uploaded_file.name, str(e)
            )
