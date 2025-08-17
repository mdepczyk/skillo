from typing import Optional

from skillo.domain.entities import Document
from skillo.domain.enums import DocumentType
from skillo.domain.schemas import (
    DocumentProcessingResponse,
    NormalizationResponse,
)
from skillo.domain.services.document_content_builder import (
    DocumentContentBuilder,
)
from skillo.domain.services.document_metadata_builder import (
    DocumentMetadataBuilder,
)


class DocumentBuilder:
    """Domain service for document assembly."""

    @staticmethod
    def build_cv_document(
        doc_id: str,
        filename: str,
        processing_response: DocumentProcessingResponse,
        normalization_response: NormalizationResponse,
        profile: str,
    ) -> Document:
        """Assemble CV document from processed components."""
        content = DocumentContentBuilder.build_cv_content(
            processing_response, normalization_response
        )

        metadata = DocumentMetadataBuilder.build_base_metadata(
            filename, processing_response, normalization_response, profile
        )

        return Document(
            id=doc_id,
            document_type=DocumentType.CV,
            content=content,
            metadata=metadata,
        )

    @staticmethod
    def build_job_document(
        doc_id: str,
        filename: str,
        processing_response: DocumentProcessingResponse,
        normalization_response: NormalizationResponse,
        profile: Optional[str] = None,
    ) -> Document:
        """Assemble Job document from processed components."""
        content = DocumentContentBuilder.build_job_content(
            processing_response, normalization_response
        )

        metadata = DocumentMetadataBuilder.build_base_metadata(
            filename, processing_response, normalization_response, profile
        )

        return Document(
            id=doc_id,
            document_type=DocumentType.JOB,
            content=content,
            metadata=metadata,
        )
