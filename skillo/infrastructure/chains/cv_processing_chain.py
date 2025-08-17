from operator import itemgetter
from typing import Any, Dict

from langchain_core.runnables import RunnableLambda, RunnableParallel

from skillo.domain.entities import Document
from skillo.domain.services import (
    DocumentAgentService,
    DocumentBuilder,
    NormalizationService,
    ProfileClassificationService,
)
from skillo.infrastructure.agents.langchain_cv_processing_agent import (
    LangChainCVProcessingAgent,
)
from skillo.infrastructure.agents.langchain_normalization_agent import (
    LangChainNormalizationAgent,
)
from skillo.infrastructure.logger import logger


class LangChainCVProcessingChain:
    """LangChain-based CV processing pipeline implementation."""

    CHAIN_NAME = "CV PROCESSING CHAIN"

    def __init__(
        self,
        cv_agent: DocumentAgentService,
        normalizer: NormalizationService,
        profile_classifier: ProfileClassificationService,
        document_builder: DocumentBuilder,
    ) -> None:
        self._cv_agent = cv_agent
        self._normalizer = normalizer
        self._profile_classifier = profile_classifier
        self._document_builder = document_builder
        self._pipeline = self._build_pipeline()

    def process_document(
        self, content: str, filename: str, doc_id: str
    ) -> Document:
        """Process single CV document through LangChain pipeline."""
        logger.info(self.CHAIN_NAME, f"Processing CV document: {filename}")

        try:
            result = self._pipeline.invoke(
                {"content": content, "filename": filename, "doc_id": doc_id}
            )

            logger.success(
                self.CHAIN_NAME,
                f"CV processing completed: {filename}",
                f"Profile: {result['profile']}, Skills: {len(result['processing_response'].skills)}",
            )

            return result["document"]  # type: ignore[no-any-return]

        except Exception as e:
            logger.error(
                self.CHAIN_NAME, f"CV processing failed: {filename}", str(e)
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
                        lambda x: self._cv_agent.process_document(x["content"])
                    ),
                    "profile": RunnableLambda(
                        lambda x: self._profile_classifier.classify_profile(
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
                    "normalization_response": self._normalizer.normalize_cv_data(
                        x["processing_response"]
                    ),
                }
            )
            | RunnableLambda(self._build_document)
        )

    def _build_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build CV document using injected DocumentBuilder."""
        document = self._document_builder.build_cv_document(
            doc_id=data["doc_id"],
            filename=data["filename"],
            processing_response=data["processing_response"],
            normalization_response=data["normalization_response"],
            profile=data["profile"],
        )

        return {**data, "document": document}


def create_cv_processing_chain(
    config: Any,
    profile_classifier: ProfileClassificationService,
    document_builder: DocumentBuilder,
) -> LangChainCVProcessingChain:
    """Factory function for CV processing chain with DI integration."""

    cv_agent = LangChainCVProcessingAgent(config)
    normalizer = LangChainNormalizationAgent(config)

    return LangChainCVProcessingChain(
        cv_agent, normalizer, profile_classifier, document_builder
    )
