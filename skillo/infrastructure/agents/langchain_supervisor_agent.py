from typing import Any, Dict

import yaml
from langchain_openai import ChatOpenAI

from skillo.domain.entities import Document
from skillo.domain.enums import MatchRecommendation
from skillo.domain.exceptions import SkilloAgentError
from skillo.domain.services import SupervisorAgentInterface
from skillo.infrastructure.agents.agent_router import (
    AgentRouter,
    RoutingDecision,
)
from skillo.infrastructure.agents.analysis_agents import AnalysisAgents
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger
from skillo.infrastructure.tools.agent_execution_tool import (
    initialize_agents,
    run_agent_analysis,
)


class LangChainSupervisorAgent(SupervisorAgentInterface):

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
        
        self.agents = AnalysisAgents(
            skills=LangChainSkillsAgent(config),
            location=LangChainLocationAgent(config),
            experience=LangChainExperienceAgent(config),
            preferences=LangChainPreferencesAgent(config),
            education=LangChainEducationAgent(config),
        )
        self.agent_router = AgentRouter(config)

        initialize_agents(self.agents)

        self.default_weights = {
            "skills_weight": 0.30,
            "location_weight": 0.15,
            "experience_weight": 0.25,
            "preferences_weight": 0.10,
            "education_weight": 0.20,
        }

    def get_agent_weights(self) -> Dict[str, float]:
        if self.app_config and hasattr(self.app_config, "AGENT_WEIGHTS"):
            return self.app_config.AGENT_WEIGHTS
        return self.default_weights

    def _get_recommendation(self, score: float) -> str:
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
        logger.info(
            self.AGENT_NAME,
            "Starting intelligent match analysis with AgentRouter",
        )

        try:
            routing_decision = self.agent_router.decide_agents(
                cv_document, job_document
            )

            logger.info(
                self.AGENT_NAME,
                f"Router selected agents: {routing_decision.agents}",
                f"Reasoning: {routing_decision.reasoning}",
            )

            results = self._execute_selected_agents(
                routing_decision, cv_document, job_document
            )

            agent_weights = self.get_agent_weights()
            final_result = self._calculate_final_result(results, agent_weights)

            logger.success(
                self.AGENT_NAME,
                f"Intelligent analysis completed: {final_result['recommendation']}",
                f"Final Score: {final_result['weighted_final_score']:.3f}",
            )

            return final_result

        except Exception as e:
            error_msg = f"Error in document analysis: {str(e)}"
            logger.error(self.AGENT_NAME, "Document analysis error", error_msg)
            raise SkilloAgentError(f"Document analysis failed: {error_msg}")

    def _execute_selected_agents(
        self,
        routing_decision: RoutingDecision,
        cv_document: Document,
        job_document: Document,
    ) -> Dict[str, Any]:
        """Execute selected agents using clean tool-based approach."""
        results = {}

        for agent_name in routing_decision.agents:
            result = run_agent_analysis.invoke(
                {
                    "agent_name": agent_name,
                    "cv_document": cv_document,
                    "job_document": job_document,
                }
            )
            results[agent_name] = result

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

        weighted_score = (
            scores["skills_score"] * agent_weights.get("skills_weight", 0.30)
            + scores["location_score"]
            * agent_weights.get("location_weight", 0.15)
            + scores["experience_score"]
            * agent_weights.get("experience_weight", 0.25)
            + scores["preferences_score"]
            * agent_weights.get("preferences_weight", 0.10)
            + scores["education_score"]
            * agent_weights.get("education_weight", 0.20)
        )

        recommendation = self._get_recommendation(weighted_score)
        explanation = self._compile_explanation(
            results, agent_weights, weighted_score
        )

        return {
            **scores,
            "weighted_final_score": weighted_score,
            "recommendation": recommendation,
            "explanation": explanation,
            "detailed_results": results,
            "agent_weights": agent_weights,
        }

    def _compile_explanation(
        self,
        results: Dict[str, Any],
        weights: Dict[str, float],
        final_score: float,
    ) -> str:
        """Compile explanation from agent results."""
        explanation_parts = [f"Overall Match Score: {final_score:.3f}"]

        for agent_name, result in results.items():
            if (
                result
                and "explanation" in result
                and not result.get("error", False)
            ):
                weight = weights.get(f"{agent_name}_weight", 0.0)
                explanation_parts.append(
                    f"{agent_name.title()} Analysis (weight {weight:.2f}): {result['explanation']}"
                )

        return " | ".join(explanation_parts)


def create_supervisor_agent(config=None) -> LangChainSupervisorAgent:
    return LangChainSupervisorAgent(config)
