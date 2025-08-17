from abc import ABC, abstractmethod
from typing import List

from skillo.domain.entities import Document
from skillo.domain.enums import DocumentType


class DocumentRepository(ABC):
    """Document repository interface."""

    @abstractmethod
    def get_documents_by_type(self, doc_type: DocumentType) -> List[Document]:
        """Get documents by type."""
        pass

    @abstractmethod
    def add_document(self, document: Document) -> bool:
        """Add document to storage."""
        pass

    @abstractmethod
    def find_similar_documents(
        self, query: str, doc_type: DocumentType, limit: int = 10
    ) -> List[Document]:
        """Find similar documents."""
        pass


class ManagementRepository(ABC):
    """Management repository interface."""

    @abstractmethod
    def reset_database(self) -> bool:
        """Reset database."""
        pass

    @abstractmethod
    def get_all_documents(self) -> List[Document]:
        """Get all documents from database."""
        pass
