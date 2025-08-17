from typing import Any, Dict

from skillo.domain.entities.agent_scores import AgentScores
from skillo.domain.entities.match_result import MatchResult
from skillo.domain.enums import MatchRecommendation


class MatchResultFactory:
    """MatchResult factory."""

    @staticmethod
    def from_analysis_result(analysis_data: Dict[str, Any]) -> MatchResult:
        """Create MatchResult from analysis data."""
        agent_scores = AgentScores(
            skills_score=analysis_data["skills_score"],
            location_score=analysis_data["location_score"],
            experience_score=analysis_data["experience_score"],
            preferences_score=analysis_data["preferences_score"],
            education_score=analysis_data["education_score"],
        )

        return MatchResult(
            cv_document=analysis_data["cv_document"],
            job_document=analysis_data["job_document"],
            weighted_final_score=analysis_data["weighted_final_score"],
            recommendation=MatchRecommendation(
                analysis_data["recommendation"]
            ),
            explanation=analysis_data["explanation"],
            agent_scores=agent_scores,
            detailed_results=analysis_data.get("detailed_results"),
        )
