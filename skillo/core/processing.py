import hashlib
import os
from typing import Any, Dict

from pypdf import PdfReader

from skillo.config import Config
from skillo.exceptions.exceptions import SkilloProcessingError


class DocumentProcessor:
    """Handle PDF document processing and text extraction"""

    def __init__(self, config: Config, cv_agent, job_agent, normalizer):
        self.config = config
        self._cv_agent = cv_agent
        self._job_agent = job_agent
        self._normalizer = normalizer

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text content from PDF file"""
        try:
            reader = PdfReader(pdf_file)

            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            raise SkilloProcessingError(f"PDF extraction failed: {str(e)}")

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
            raise SkilloProcessingError(f"Invalid file type '{file_type}', only PDF files are supported")

        os.makedirs(save_dir, exist_ok=True)

        file_path = os.path.join(save_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path

    def process_document(
        self, uploaded_file, file_type: str
    ) -> Dict[str, Any]:
        """Process uploaded PDF document with Document Processing and Normalization agents"""
        from skillo.agents import (
            LangChainCVProcessingAgent,
            LangChainJobProcessingAgent, 
            LangChainNormalizationAgent
        )

        text_content = self.extract_text_from_pdf(uploaded_file)

        if not text_content:
            raise SkilloProcessingError(f"Empty document '{uploaded_file.name}' - no text could be extracted")

        doc_id = self.generate_document_id(text_content, uploaded_file.name)

        file_path = self.save_uploaded_file(uploaded_file, file_type)

        metadata = {
            "filename": uploaded_file.name,
            "file_path": file_path,
            "file_size": len(uploaded_file.getvalue()),
            "char_count": len(text_content),
            "word_count": len(text_content.split()),
        }

        try:
            if file_type == "cv":
                processed_document = self._process_cv_document(
                    text_content, metadata
                )
            elif file_type == "job":
                processed_document = self._process_job_document(
                    text_content, metadata
                )
            else:
                raise SkilloProcessingError(f"Invalid file type '{file_type}' in batch processing")

            processed_document["id"] = doc_id

            return processed_document

        except Exception as e:
            raise SkilloProcessingError(f"Processing '{uploaded_file.name}' failed: {str(e)}")

    def _process_cv_document(
        self, cv_content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process CV document using Document Processing and Normalization agents."""        
        try:
            structured_cv = self._cv_agent.process_cv(cv_content)
            normalized_cv = self._normalizer.normalize_cv_data(structured_cv)

            processed_document = {
                "content": cv_content,
                "structured_data": structured_cv,
                "normalized_data": normalized_cv,
                "metadata": metadata,
                "document_type": "cv",
            }

            return processed_document

        except Exception as e:
            raise SkilloProcessingError(f"CV document processing failed: {str(e)}") from e

    def _process_job_document(
        self, job_content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process job posting document using Document Processing and Normalization agents."""        
        try:
            structured_job = self._job_agent.process_job_posting(job_content)
            normalized_job = self._normalizer.normalize_job_data(structured_job)

            processed_document = {
                "content": job_content,
                "structured_data": structured_job,
                "normalized_data": normalized_job,
                "metadata": metadata,
                "document_type": "job",
            }

            return processed_document

        except Exception as e:
            raise SkilloProcessingError(f"Job document processing failed: {str(e)}") from e
