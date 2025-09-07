from skillo.domain.entities import Document
from skillo.domain.exceptions import SkilloProcessingError
from skillo.infrastructure.chains import LangChainJobProcessingChain
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.document_processing.base_processor import (
    BaseDocumentProcessor,
)


class JobDocumentProcessor(BaseDocumentProcessor):
    """Processes job documents."""

    def __init__(
        self,
        config: Config,
        job_chain: LangChainJobProcessingChain,
    ) -> None:
        super().__init__(config)
        self._job_chain = job_chain

    def process_document_content(
        self, content: str, filename: str, doc_id: str
    ) -> Document:
        """Process job document content using LangChain chain."""
        try:
            chain_input = {
                "content": content,
                "filename": filename,
                "doc_id": doc_id,
            }

            result = self._job_chain.invoke(chain_input)

            return result

        except Exception as e:
            raise SkilloProcessingError(
                f"Job document processing failed: {str(e)}"
            ) from e
