from dataclasses import dataclass
from typing import Any, Dict, Optional

from skillo.domain.entities.agent_scores import AgentScores
from skillo.domain.entities.document import Document
from skillo.domain.enums import MatchRecommendation


@dataclass
class MatchResult:
    """CV-Job matching result."""

    cv_document: Optional[Document]
    job_document: Optional[Document]
    weighted_final_score: float
    recommendation: MatchRecommendation
    explanation: str
    agent_scores: AgentScores
    detailed_results: Optional[Dict[str, Any]] = None
