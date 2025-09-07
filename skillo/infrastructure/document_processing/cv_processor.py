from skillo.domain.entities import Document
from skillo.domain.exceptions import SkilloProcessingError
from skillo.infrastructure.chains import LangChainCVProcessingChain
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.document_processing.base_processor import (
    BaseDocumentProcessor,
)


class CVDocumentProcessor(BaseDocumentProcessor):
    """Processes CV documents."""

    def __init__(
        self,
        config: Config,
        cv_chain: LangChainCVProcessingChain,
    ) -> None:
        super().__init__(config)
        self._cv_chain = cv_chain

    def process_document_content(
        self, content: str, filename: str, doc_id: str
    ) -> Document:
        """Process CV document content using LangChain chain."""
        try:
            chain_input = {
                "content": content,
                "filename": filename,
                "doc_id": doc_id,
            }

            result = self._cv_chain.invoke(chain_input)

            return result

        except Exception as e:
            raise SkilloProcessingError(
                f"CV document processing failed: {str(e)}"
            ) from e
