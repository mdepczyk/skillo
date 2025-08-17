import hashlib
import os
from abc import ABC, abstractmethod

from pypdf import PdfReader

from skillo.domain.entities import Document
from skillo.domain.exceptions import SkilloProcessingError
from skillo.infrastructure.config.settings import Config


class BaseDocumentProcessor(ABC):
    """Base class for document processors."""

    def __init__(self, config: Config, normalizer):
        self.config = config
        self._normalizer = normalizer

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF."""
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise SkilloProcessingError(f"PDF extraction failed: {str(e)}")

    def generate_document_id(self, content: str, filename: str) -> str:
        """Generate document ID."""
        combined = f"{filename}_{content[:100]}"
        return hashlib.md5(combined.encode()).hexdigest()

    def save_uploaded_file(self, uploaded_file, save_dir: str) -> str:
        """Save uploaded file and return path."""
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path

    @abstractmethod
    def process_document_content(
        self, content: str, filename: str, doc_id: str
    ) -> Document:
        """Process document content. Must be implemented by subclasses."""
        pass