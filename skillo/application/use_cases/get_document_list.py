from typing import List, Optional

from skillo.application.dto import DocumentDto
from skillo.application.mappers import DTOMapper
from skillo.application.protocols import FileSystemProtocol
from skillo.domain.enums import DocumentType
from skillo.domain.repositories import DocumentRepository


class DocumentTypeError(ValueError):
    """Invalid document type provided."""

    pass


class GetDocumentList:
    """Get document list with file paths and metadata."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        filesystem: FileSystemProtocol,
        cv_upload_dir: str,
        job_upload_dir: str,
    ):
        """Initialize with dependencies."""
        self._document_repository = document_repository
        self._filesystem = filesystem
        self._cv_upload_dir = cv_upload_dir
        self._job_upload_dir = job_upload_dir

    def get_file_path(
        self, filename: str, document_type: DocumentType
    ) -> Optional[str]:
        """Get file path for document."""
        if document_type == DocumentType.CV:
            file_path = self._filesystem.join_path(
                self._cv_upload_dir, filename
            )
        else:
            file_path = self._filesystem.join_path(
                self._job_upload_dir, filename
            )

        return file_path if self._filesystem.file_exists(file_path) else None

    def execute_dto(
        self, document_type_str: Optional[str] = None
    ) -> List[DocumentDto]:
        """Get document list as DTOs. Accepts string, converts to enum internally."""
        if document_type_str:
            document_type = self._validate_document_type(document_type_str)
        else:
            document_type = None

        if document_type == DocumentType.CV:
            documents = self._document_repository.get_documents_by_type(
                DocumentType.CV
            )
        elif document_type == DocumentType.JOB:
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

        return DTOMapper.documents_to_dtos(documents)

    def _validate_document_type(self, type_str: str) -> DocumentType:
        """Validate and convert string to DocumentType enum."""
        try:
            return DocumentType(type_str)
        except ValueError:
            valid_types = ", ".join([dt.value for dt in DocumentType])
            raise DocumentTypeError(
                f"Invalid document type '{type_str}'. Valid types: {valid_types}"
            )
