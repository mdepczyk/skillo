import os
from typing import Dict, List, Optional

from skillo.application.dto import DocumentDto
from skillo.domain.enums import DocumentType
from skillo.domain.repositories import DocumentRepository


class GetDocumentList:
    """Get document list with file paths and metadata."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        cv_upload_dir: str,
        job_upload_dir: str,
    ):
        """Initialize with dependencies."""
        self._document_repository = document_repository
        self._cv_upload_dir = cv_upload_dir
        self._job_upload_dir = job_upload_dir

    def get_cv_list(self) -> List[Dict[str, str]]:
        """Get CV document list."""
        try:
            documents = self._document_repository.get_documents_by_type(
                DocumentType.CV
            )

            return [
                {
                    "document_id": doc.id,
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "file_path": os.path.join(
                        self._cv_upload_dir,
                        doc.metadata.get("filename", ""),
                    ),
                    "name": doc.metadata.get("name", "Unknown"),
                    "contact": doc.metadata.get("contact", "Not specified"),
                    "location": doc.metadata.get("location", "Not specified"),
                    "skills": doc.metadata.get("skills", ""),
                    "profile": doc.metadata.get("job_title", "Unknown"),
                    "exists": os.path.exists(
                        os.path.join(
                            self._cv_upload_dir,
                            doc.metadata.get("filename", ""),
                        )
                    ),
                }
                for doc in documents
            ]
        except Exception:
            return []

    def get_job_list(self) -> List[Dict[str, str]]:
        """Get job document list."""
        try:
            documents = self._document_repository.get_documents_by_type(
                DocumentType.JOB
            )

            return [
                {
                    "document_id": doc.id,
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "file_path": os.path.join(
                        self._job_upload_dir,
                        doc.metadata.get("filename", ""),
                    ),
                    "job_title": doc.metadata.get(
                        "job_title", "Not specified"
                    ),
                    "company": doc.metadata.get("contact", "Not specified"),
                    "location": doc.metadata.get("location", "Not specified"),
                    "required_skills": doc.metadata.get("skills", ""),
                    "exists": os.path.exists(
                        os.path.join(
                            self._job_upload_dir,
                            doc.metadata.get("filename", ""),
                        )
                    ),
                }
                for doc in documents
            ]
        except Exception:
            return []

    def get_file_path(
        self, filename: str, document_type: DocumentType
    ) -> Optional[str]:
        """Get file path for document."""
        if document_type == DocumentType.CV:
            file_path = os.path.join(self._cv_upload_dir, filename)
        else:
            file_path = os.path.join(self._job_upload_dir, filename)

        return file_path if os.path.exists(file_path) else None

    def execute_dto(
        self, document_type: Optional[str] = None
    ) -> List[DocumentDto]:
        """Get document list as DTOs."""
        if document_type == "cv":
            documents = self._document_repository.get_documents_by_type(
                DocumentType.CV
            )
        elif document_type == "job":
            documents = self._document_repository.get_documents_by_type(
                DocumentType.JOB
            )
        else:
            cv_documents = self._document_repository.get_documents_by_type(
                DocumentType.CV
            )
            job_documents = self._document_repository.get_documents_by_type(
                DocumentType.JOB
            )
            documents = cv_documents + job_documents

        return [self._convert_to_document_dto(doc) for doc in documents]

    def _convert_to_document_dto(self, document) -> DocumentDto:
        """Convert Document to DTO."""
        return DocumentDto(
            id=document.id,
            document_type=document.document_type.value,
            content=document.content,
            metadata=document.metadata,
        )
