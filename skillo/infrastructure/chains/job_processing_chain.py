from operator import itemgetter
from typing import Any, Dict

from langchain_core.runnables import RunnableLambda, RunnableParallel

from skillo.domain.entities import Document
from skillo.domain.services import (
    DocumentAgentService,
    DocumentBuilder,
    NormalizationService,
)
from skillo.infrastructure.agents.langchain_job_processing_agent import (
    LangChainJobProcessingAgent,
)
from skillo.infrastructure.agents.langchain_normalization_agent import (
    LangChainNormalizationAgent,
)
from skillo.infrastructure.logger import logger


class LangChainJobProcessingChain:
    """LangChain-based Job processing pipeline implementation."""

    CHAIN_NAME = "JOB PROCESSING CHAIN"

    def __init__(
        self,
        job_agent: DocumentAgentService,
        normalizer: NormalizationService,
        document_builder: DocumentBuilder,
    ) -> None:
        self._job_agent = job_agent
        self._normalizer = normalizer
        self._document_builder = document_builder
        self._pipeline = self._build_pipeline()

    def process_document(
        self, content: str, filename: str, doc_id: str
    ) -> Document:
        """Process single Job document through LangChain pipeline."""
        logger.info(self.CHAIN_NAME, f"Processing Job document: {filename}")

        try:
            result = self._pipeline.invoke(
                {"content": content, "filename": filename, "doc_id": doc_id}
            )

            logger.success(
                self.CHAIN_NAME,
                f"Job processing completed: {filename}",
                f"Required skills: {len(result['processing_response'].skills)}",
            )

            return result["document"]  # type: ignore[no-any-return]

        except Exception as e:
            logger.error(
                self.CHAIN_NAME, f"Job processing failed: {filename}", str(e)
            )
            raise

    def invoke(self, input_data: Dict[str, Any]) -> Document:
        """Simple invoke method for compatibility."""
        return self.process_document(
            input_data["content"], input_data["filename"], input_data["doc_id"]
        )

    def _build_pipeline(self) -> Any:
        """Build LangChain pipeline for parallel LLM + ML processing."""
        return (
            RunnableParallel(
                {  # type: ignore[arg-type]
                    "processing_response": RunnableLambda(
                        lambda x: self._job_agent.process_document(
                            x["content"]
                        )
                    ),
                    "filename": itemgetter("filename"),
                    "doc_id": itemgetter("doc_id"),
                    "content": itemgetter("content"),
                }
            )
            | RunnableLambda(
                lambda x: {
                    **x,
                    "normalization_response": self._normalizer.normalize_job_data(
                        x["processing_response"]
                    ),
                }
            )
            | RunnableLambda(self._build_document)
        )

    def _build_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build Job document using injected DocumentBuilder."""
        document = self._document_builder.build_job_document(
            doc_id=data["doc_id"],
            filename=data["filename"],
            processing_response=data["processing_response"],
            normalization_response=data["normalization_response"],
            profile=None,
        )

        return {**data, "document": document}


def create_job_processing_chain(
    config: Any, document_builder: DocumentBuilder
) -> LangChainJobProcessingChain:
    """Factory function for Job processing chain with DI integration."""

    job_agent = LangChainJobProcessingAgent(config)
    normalizer = LangChainNormalizationAgent(config)

    return LangChainJobProcessingChain(job_agent, normalizer, document_builder)
