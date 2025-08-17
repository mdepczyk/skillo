from typing import List

from skillo.domain.entities import Document
from skillo.domain.enums import DocumentType
from skillo.domain.exceptions import SkilloRepositoryError
from skillo.domain.repositories import ManagementRepository
from skillo.infrastructure.repositories.chroma_document_repository import (
    ChromaDocumentRepository,
)


class ChromaManagementRepository(ManagementRepository):
    """Chroma implementation of ManagementRepository interface."""

    def __init__(self, document_repository: ChromaDocumentRepository):
        """Initialize with document repository for access to vectorstore."""
        self._document_repository = document_repository

    def reset_database(self) -> bool:
        """Reset the entire database."""
        try:
            self._document_repository.vectorstore.delete_collection()
            self._document_repository._initialize_vectorstore()
            return True

        except Exception as e:
            raise SkilloRepositoryError(f"Failed to reset database: {str(e)}")

    def get_all_documents(self) -> List[Document]:
        """Get all documents from database for management operations."""
        try:
            cv_docs = self._document_repository.get_documents_by_type(
                DocumentType.CV
            )
            job_docs = self._document_repository.get_documents_by_type(
                DocumentType.JOB
            )

            return cv_docs + job_docs

        except Exception as e:
            error_msg = f"Failed to get all documents: {str(e)}"
            raise SkilloRepositoryError(error_msg)
