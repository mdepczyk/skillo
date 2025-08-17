from dataclasses import dataclass
from typing import Any, Dict, List

from skillo.domain.enums import DocumentType


class UiHelpers:
    """UI formatting helpers."""

    @staticmethod
    def format_score(score: float, as_percentage: bool = True) -> str:
        """Format a score for display."""
        if as_percentage:
            return f"{score:.1%}"
        return f"{score:.3f}"


class LogLevelDto:
    """Log level constants."""

    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class LogEntryDto:
    """Log entry DTO."""

    timestamp: str
    level: str
    agent: str
    action: str
    details: str


@dataclass
class DocumentDto:
    """Document DTO."""

    id: str
    document_type: DocumentType
    content: str
    metadata: Dict[str, Any]


@dataclass
class MatchResultDto:
    """Match result DTO."""

    cv_id: str
    job_id: str
    cv_filename: str
    job_filename: str
    cv_metadata: Dict[str, Any]
    job_metadata: Dict[str, Any]
    weighted_final_score: float
    recommendation: str
    explanation: str
    agent_scores: Dict[str, float]
    detailed_results: Dict[str, Any]


@dataclass
class StatisticsDto:
    """Statistics DTO."""

    total_documents: int
    cv_count: int
    job_count: int
    cv_documents: List[DocumentDto]
    job_documents: List[DocumentDto]


@dataclass
class ConfigDto:
    """Configuration DTO."""

    chroma_db_path: str
    collection_name: str
    embedding_model: str
    min_match_score: float
    top_candidates_count: int
    agent_weights: Dict[str, float]


@dataclass
class EventDto:
    """Application event DTO."""

    event_type: str
    message: str
    level: str
