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


class JobDocumentProcessor(BaseDocumentProcessor):
    """Processes job documents."""

    def __init__(self, config, job_agent, normalizer):
        super().__init__(config, normalizer)
        self._job_agent = job_agent

    def process_document_content(
        self, content: str, filename: str, doc_id: str
    ) -> Document:
        """Process job document content."""
        try:
            processing_response = self._job_agent.process_job_posting(content)
            normalization_response = self._normalizer.normalize_job_data(
                processing_response
            )

            metadata = DocumentMetadataBuilder.build_base_metadata(
                filename, processing_response, normalization_response
            )

            document_content = DocumentContentBuilder.build_job_content(
                processing_response, normalization_response
            )

            return Document(
                id=doc_id,
                document_type=DocumentType.JOB,
                content=document_content,
                metadata=metadata,
            )

        except Exception as e:
            raise SkilloProcessingError(
                f"Job document processing failed: {str(e)}"
            ) from e