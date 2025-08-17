from typing import Any, Dict

import yaml  # type: ignore
from langchain_openai import ChatOpenAI

from skillo.domain.entities import Document
from skillo.domain.enums import MatchRecommendation
from skillo.domain.exceptions import SkilloAgentError
from skillo.domain.services import SupervisorAgentInterface
from skillo.infrastructure.agents.langchain_education_agent import (
    LangChainEducationAgent,
)
from skillo.infrastructure.agents.langchain_experience_agent import (
    LangChainExperienceAgent,
)
from skillo.infrastructure.agents.langchain_location_agent import (
    LangChainLocationAgent,
)
from skillo.infrastructure.agents.langchain_preferences_agent import (
    LangChainPreferencesAgent,
)
from skillo.infrastructure.agents.langchain_skills_agent import (
    LangChainSkillsAgent,
)
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger


class LangChainSupervisorAgent(SupervisorAgentInterface):
    """Simplified supervisor agent without legacy routing complexity."""

    AGENT_NAME = "SUPERVISOR AGENT"

    def __init__(self, config: Config):
        """Initialize with config."""
        prompts_dir = config.PROMPTS_DIR
        prompt_template = f"{prompts_dir}/supervisor_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["supervisor_analysis"]

        self.app_config = config

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        )

        self.skills_agent = LangChainSkillsAgent(config)
        self.location_agent = LangChainLocationAgent(config)
        self.experience_agent = LangChainExperienceAgent(config)
        self.preferences_agent = LangChainPreferencesAgent(config)
        self.education_agent = LangChainEducationAgent(config)

        self.default_weights = {
            "skills_weight": 0.30,
            "location_weight": 0.15,
            "experience_weight": 0.25,
            "preferences_weight": 0.10,
            "education_weight": 0.20,
        }

    def get_agent_weights(self) -> Dict[str, float]:
        """Get agent weights from config or defaults."""
        if self.app_config and hasattr(self.app_config, "AGENT_WEIGHTS"):
            return self.app_config.AGENT_WEIGHTS
        return self.default_weights

    def _get_recommendation(self, score: float) -> str:
        """Convert score to recommendation enum."""
        if score >= 0.8:
            return MatchRecommendation.STRONG_MATCH.value
        elif score >= 0.6:
            return MatchRecommendation.GOOD_MATCH.value
        elif score >= 0.4:
            return MatchRecommendation.FAIR_MATCH.value
        elif score >= 0.2:
            return MatchRecommendation.POOR_MATCH.value
        else:
            return MatchRecommendation.NO_MATCH.value

    def analyze_match(
        self, cv_document: Document, job_document: Document
    ) -> Dict[str, Any]:
        """Analyze CV-job match using all agents."""
        logger.info(self.AGENT_NAME, "Starting comprehensive match analysis")

        try:
            results = self._execute_all_agents(cv_document, job_document)

            agent_weights = self.get_agent_weights()
            final_result = self._calculate_final_result(results, agent_weights)

            logger.success(
                self.AGENT_NAME,
                f"Analysis completed: {final_result['recommendation']}",
                f"Score: {final_result['weighted_final_score']:.3f}",
            )

            return final_result

        except Exception as e:
            error_msg = f"Error in document analysis: {str(e)}"
            logger.error(self.AGENT_NAME, "Document analysis error", error_msg)
            raise SkilloAgentError(f"Document analysis failed: {error_msg}")

    def _execute_all_agents(
        self, cv_document: Document, job_document: Document
    ) -> Dict[str, Any]:
        """Execute all analysis agents directly."""
        results: Dict[str, Any] = {}

        try:
            results["skills"] = self.skills_agent.analyze_skills_match(
                cv_document.content, job_document.content
            )
            results["location"] = self.location_agent.analyze_location_match(
                cv_document.content, job_document.content
            )
            results["experience"] = (
                self.experience_agent.analyze_experience_match(
                    cv_document.content, job_document.content
                )
            )
            results["preferences"] = (
                self.preferences_agent.analyze_preferences_match(
                    cv_document.content, job_document.content
                )
            )
            results["education"] = (
                self.education_agent.analyze_education_match(
                    cv_document.content, job_document.content
                )
            )
        except Exception as e:
            logger.error(self.AGENT_NAME, "Agent execution failed", str(e))
            raise

        return results

    def _calculate_final_result(
        self, results: Dict[str, Any], agent_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate final weighted score and compile result."""

        scores = {
            "skills_score": results.get("skills", {}).get("score", 0.0),
            "location_score": results.get("location", {}).get("score", 0.0),
            "experience_score": results.get("experience", {}).get(
                "score", 0.0
            ),
            "preferences_score": results.get("preferences", {}).get(
                "score", 0.0
            ),
            "education_score": results.get("education", {}).get("score", 0.0),
        }

        weighted_final_score = (
            scores["skills_score"] * agent_weights["skills_weight"]
            + scores["location_score"] * agent_weights["location_weight"]
            + scores["experience_score"] * agent_weights["experience_weight"]
            + scores["preferences_score"] * agent_weights["preferences_weight"]
            + scores["education_score"] * agent_weights["education_weight"]
        )

        recommendation = self._get_recommendation(weighted_final_score)

        explanations = []
        for agent_name, result in results.items():
            if isinstance(result, dict) and "explanation" in result:
                explanations.append(
                    f"{agent_name.title()}: {result['explanation']}"
                )

        return {
            **scores,
            "weighted_final_score": weighted_final_score,
            "recommendation": recommendation,
            "explanation": "; ".join(explanations),
            "agent_weights": agent_weights,
            "detailed_results": results,
        }
