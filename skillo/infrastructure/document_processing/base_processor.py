import hashlib
import os
from abc import ABC, abstractmethod
from typing import Any

import fitz  # type: ignore

from skillo.domain.entities import Document
from skillo.domain.exceptions import SkilloProcessingError
from skillo.infrastructure.config.settings import Config


class BaseDocumentProcessor(ABC):
    """Base class for document processors."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def extract_text_from_pdf(self, pdf_file: Any) -> str:
        """Extract text from PDF with links replaced inline."""
        try:
            return self._extract_with_pymupdf(pdf_file)
        except Exception as e:
            raise SkilloProcessingError(f"PDF extraction failed: {str(e)}")

    def _extract_with_pymupdf(self, pdf_file: Any) -> str:
        """Extract text with links using PyMuPDF."""
        pdf_file.seek(0)
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")

        text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()

            links = page.get_links()
            for link in links:
                if "uri" in link and "from" in link:
                    rect = link["from"]
                    link_text = page.get_textbox(rect).strip()
                    url = link["uri"]

                    if link_text and url:
                        enhanced_text = f"{link_text} ({url})"
                        page_text = page_text.replace(link_text, enhanced_text)

            text += page_text + "\n"

        doc.close()
        return text.strip()

    def generate_document_id(self, content: str, filename: str) -> str:
        """Generate document ID."""
        combined = f"{filename}_{content[:100]}"
        return hashlib.md5(combined.encode()).hexdigest()

    def save_uploaded_file(self, uploaded_file: Any, save_dir: str) -> str:
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
