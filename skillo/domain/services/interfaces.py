from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Protocol

from skillo.domain.entities import Document
from skillo.domain.schemas import (
    DocumentProcessingResponse,
    NormalizationResponse,
)


class SupervisorAgentInterface(ABC):
    """Supervisor agent interface."""

    @abstractmethod
    def analyze_match(
        self, cv_document: Document, job_document: Document
    ) -> Dict[str, Any]:
        """Analyze CV-job match."""
        pass


class ProcessingInput:
    """Input for document processing pipeline."""

    def __init__(self, content: str, filename: str, doc_id: str):
        self.content = content
        self.filename = filename
        self.doc_id = doc_id


class DocumentProcessingPipeline(Protocol):
    """Domain interface for document processing pipeline."""

    def process_document(
        self, content: str, filename: str, doc_id: str
    ) -> Document:
        """Process single document through pipeline."""
        ...


class ProfileClassificationService(Protocol):
    """Domain interface for ML profile classification."""

    def classify_profile(self, content: str) -> str:
        """Classify document profile (e.g., 'Software Engineer', 'Data Scientist')."""
        ...


class DocumentAgentService(Protocol):
    """Domain interface for LLM-based document parsing."""

    def process_document(self, content: str) -> DocumentProcessingResponse:
        """Parse document content using LLM."""
        ...


class NormalizationService(Protocol):
    """Domain interface for data normalization."""

    def normalize_cv_data(
        self, processing_response: DocumentProcessingResponse
    ) -> NormalizationResponse:
        """Normalize and standardize parsed CV data."""
        ...

    def normalize_job_data(
        self, processing_response: DocumentProcessingResponse
    ) -> NormalizationResponse:
        """Normalize and standardize parsed job data."""
        ...


class ParallelExecutionService(Protocol):
    """Domain interface for parallel task execution."""

    def execute_tasks_with_progress(
        self,
        tasks: List[Any],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Any]:
        """Execute tasks in parallel with progress tracking."""
        ...
