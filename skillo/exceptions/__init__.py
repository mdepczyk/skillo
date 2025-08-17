"""Custom exceptions for Skillo application."""

from .configuration import ConfigurationError, MissingEnvironmentVariableError

from .document_processing import (
    PDFExtractionError,
    FileUploadError,
    DocumentProcessingError,
    InvalidFileTypeError,
    EmptyDocumentError,
)

from .vectorstore import (
    VectorStoreInitializationError,
    DocumentStorageError,
    DocumentRetrievalError,
    EmbeddingGenerationError,
    CollectionNotFoundError,
    SimilarityCalculationError,
)

from .agent import (
    LLMResponseError,
    PromptLoadingError,
    AgentProcessingError,
    StructuredOutputError,
    AgentCoordinationError,
)

from .matching import (
    MatchAnalysisError,
    ScoreCalculationError,
    PrefilteringError,
    StructuredDataMissingError,
    MatchingConfigurationError,
    MatchingProcessError,
)

__all__ = [
    "ConfigurationError",
    "MissingEnvironmentVariableError",
    "PDFExtractionError",
    "FileUploadError",
    "DocumentProcessingError",
    "InvalidFileTypeError",
    "EmptyDocumentError",
    "VectorStoreInitializationError",
    "DocumentStorageError",
    "DocumentRetrievalError",
    "EmbeddingGenerationError",
    "CollectionNotFoundError",
    "SimilarityCalculationError",
    "LLMResponseError",
    "PromptLoadingError",
    "AgentProcessingError",
    "StructuredOutputError",
    "AgentCoordinationError",
    "MatchAnalysisError",
    "ScoreCalculationError",
    "PrefilteringError",
    "StructuredDataMissingError",
    "MatchingConfigurationError",
    "MatchingProcessError",
]
