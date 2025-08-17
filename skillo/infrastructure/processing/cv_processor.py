from skillo.domain.entities import Document
from skillo.domain.enums import DocumentType
from skillo.domain.exceptions import SkilloProcessingError
from skillo.infrastructure.processing.base_processor import (
    BaseDocumentProcessor,
)
from skillo.infrastructure.processing.document_content_builder import (
    DocumentContentBuilder,
)
from skillo.infrastructure.processing.document_metadata_builder import (
    DocumentMetadataBuilder,
)


class CVDocumentProcessor(BaseDocumentProcessor):
    """Processes CV documents."""

    def __init__(self, config, cv_agent, normalizer):
        super().__init__(config, normalizer)
        self._cv_agent = cv_agent

    def process_document_content(
        self, content: str, filename: str, doc_id: str
    ) -> Document:
        """Process CV document content."""
        try:
            processing_response, profile = self._cv_agent.process_cv(content)
            normalization_response = self._normalizer.normalize_cv_data(
                processing_response, profile
            )

            metadata = DocumentMetadataBuilder.build_base_metadata(
                filename, processing_response, normalization_response, profile
            )

            document_content = DocumentContentBuilder.build_cv_content(
                processing_response, normalization_response
            )

            return Document(
                id=doc_id,
                document_type=DocumentType.CV,
                content=document_content,
                metadata=metadata,
            )

        except Exception as e:
            raise SkilloProcessingError(
                f"CV document processing failed: {str(e)}"
            ) from e