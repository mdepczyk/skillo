import os
from typing import Any, Dict

import yaml
from langchain_openai import ChatOpenAI

from skillo.agents.langchain_experience_agent import LangChainExperienceAgent
from skillo.agents.langchain_location_agent import LangChainLocationAgent
from skillo.agents.langchain_preferences_agent import LangChainPreferencesAgent
from skillo.agents.langchain_semantic_agent import LangChainSemanticAgent
from skillo.agents.langchain_skills_agent import LangChainSkillsAgent
from skillo.enums import MatchRecommendation
from skillo.exceptions import AgentCoordinationError
from skillo.utils.logger import logger


class LangChainSupervisorAgent:

    AGENT_NAME = "SUPERVISOR AGENT"

    def __init__(self, config=None, vectorstore=None):
        prompts_dir = os.getenv("PROMPTS_DIR")
        prompt_template = f"{prompts_dir}/supervisor_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["supervisor_analysis"]

        self.app_config = config

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        )

        self.skills_agent = LangChainSkillsAgent()
        self.location_agent = LangChainLocationAgent()
        self.experience_agent = LangChainExperienceAgent()
        self.preferences_agent = LangChainPreferencesAgent()
        self.semantic_agent = LangChainSemanticAgent(vectorstore=vectorstore)

        self.default_weights = {
            "skills_weight": 0.30,
            "location_weight": 0.15,
            "experience_weight": 0.25,
            "preferences_weight": 0.10,
            "semantic_weight": 0.20,
        }

    def get_agent_weights(self) -> Dict[str, float]:
        if self.app_config and hasattr(self.app_config, "agent_weights"):
            return self.app_config.agent_weights
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

    def analyze_match_with_structured_data(
        self, cv_structured: Dict[str, Any], job_structured: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(
            self.AGENT_NAME,
            "Starting enhanced match analysis with structured data",
        )

        try:
            results = {}
            agent_weights = self.get_agent_weights()

            logger.info(
                self.AGENT_NAME, "Running Skills Agent with section data"
            )
            cv_sections = cv_structured.get("sections", {})
            job_sections = job_structured.get("sections", {})

            cv_skills_section = cv_sections.get("skills", "")
            job_skills_section = job_sections.get("required_skills", "")

            skills_cv_content = f"Skills: {cv_skills_section}"
            skills_job_content = f"Required Skills: {job_skills_section}"

            skills_result = self.skills_agent.analyze_skills_match(
                skills_cv_content, skills_job_content
            )
            results["skills"] = skills_result
            skills_score = skills_result.get("score", 0.0)

            logger.info(
                self.AGENT_NAME, "Running Location Agent with section data"
            )
            cv_location_section = cv_sections.get("location", "Not specified")
            job_location_section = job_sections.get(
                "location", "Not specified"
            )

            location_cv_content = (
                f"Location: {cv_location_section}\nRemote Work: Not specified"
            )
            location_job_content = (
                f"Location: {job_location_section}\nRemote Work: Not specified"
            )

            location_result = self.location_agent.analyze_location_match(
                location_cv_content, location_job_content
            )
            results["location"] = location_result
            location_score = location_result.get("score", 0.0)

            logger.info(
                self.AGENT_NAME, "Running Experience Agent with section data"
            )
            cv_experience_section = cv_sections.get(
                "experience", "Not specified"
            )
            job_experience_section = job_sections.get(
                "experience_requirements", "Not specified"
            )

            experience_cv_content = (
                f"Level: Not specified\nDetails: {cv_experience_section}"
            )
            experience_job_content = f"Required Level: Not specified\nRequirements: {job_experience_section}"

            experience_result = self.experience_agent.analyze_experience_match(
                experience_cv_content, experience_job_content
            )
            results["experience"] = experience_result
            experience_score = experience_result.get("score", 0.0)

            logger.info(
                self.AGENT_NAME, "Running Preferences Agent with section data"
            )
            cv_preferences_section = cv_sections.get(
                "preferences", "Not specified"
            )
            job_culture_section = job_sections.get("culture_preferences", "")

            preferences_cv_content = f"Preferences: {cv_preferences_section}"
            preferences_job_content = f"Culture: {job_culture_section}"

            preferences_result = (
                self.preferences_agent.analyze_preferences_match(
                    preferences_cv_content, preferences_job_content
                )
            )
            results["preferences"] = preferences_result
            preferences_score = preferences_result.get("score", 0.0)

            logger.info(
                self.AGENT_NAME, "Running Semantic Agent with section data"
            )
            cv_sections = cv_structured.get("sections", {})
            job_sections = job_structured.get("sections", {})

            semantic_result = self.semantic_agent.analyze_semantic_similarity(
                cv_sections, job_sections
            )
            results["semantic"] = semantic_result
            semantic_score = semantic_result.get("score", 0.0)

            weighted_score = (
                skills_score * agent_weights["skills_weight"]
                + location_score * agent_weights["location_weight"]
                + experience_score * agent_weights["experience_weight"]
                + preferences_score * agent_weights["preferences_weight"]
                + semantic_score * agent_weights["semantic_weight"]
            )

            recommendation = self._get_recommendation(weighted_score)

            explanation = self._compile_enhanced_explanation(
                results,
                agent_weights,
                weighted_score,
                cv_structured,
                job_structured,
            )

            final_result = {
                "skills_score": skills_score,
                "location_score": location_score,
                "experience_score": experience_score,
                "preferences_score": preferences_score,
                "semantic_score": semantic_score,
                "weighted_final_score": weighted_score,
                "recommendation": recommendation,
                "explanation": explanation,
                "detailed_results": results,
                "agent_weights": agent_weights,
                "structured_insights": {
                    "cv_skills_section": cv_skills_section,
                    "job_skills_section": job_skills_section,
                    "cv_experience_section": cv_experience_section,
                    "job_experience_section": job_experience_section,
                    "cv_location_section": cv_location_section,
                    "job_location_section": job_location_section,
                },
            }

            logger.success(
                self.AGENT_NAME,
                f"Match analysis completed: {recommendation}",
                f"Final Score: {weighted_score:.3f}",
            )

            return final_result

        except Exception as e:
            error_msg = f"Error in structured data analysis: {str(e)}"
            logger.error(
                self.AGENT_NAME, "Structured data analysis error", error_msg
            )
            raise AgentCoordinationError("structured data analysis", error_msg)

    def _compile_enhanced_explanation(
        self,
        results: Dict[str, Any],
        weights: Dict[str, float],
        final_score: float,
        cv_structured: Dict[str, Any],
        job_structured: Dict[str, Any],
    ) -> str:
        explanation_parts = [f"Overall Match Score: {final_score:.3f}"]

        cv_title = cv_structured.get("normalized_data", {}).get(
            "normalized_job_title", "CV"
        )
        job_title = job_structured.get("normalized_data", {}).get(
            "normalized_job_title", "Position"
        )
        explanation_parts.append(f"Matching {cv_title} with {job_title}")

        if "skills" in results:
            skills_exp = results["skills"].get("explanation", "No explanation")
            explanation_parts.append(
                f"Skills Analysis (weight {weights['skills_weight']:.2f}): {skills_exp}"
            )

        if "location" in results:
            location_exp = results["location"].get(
                "explanation", "No explanation"
            )
            explanation_parts.append(
                f"Location Analysis (weight {weights['location_weight']:.2f}): {location_exp}"
            )

        if "experience" in results:
            experience_exp = results["experience"].get(
                "explanation", "No explanation"
            )
            explanation_parts.append(
                f"Experience Analysis (weight {weights['experience_weight']:.2f}): {experience_exp}"
            )

        if "preferences" in results:
            preferences_exp = results["preferences"].get(
                "explanation", "No explanation"
            )
            explanation_parts.append(
                f"Preferences Analysis (weight {weights['preferences_weight']:.2f}): {preferences_exp}"
            )

        if "semantic" in results:
            semantic_exp = results["semantic"].get(
                "explanation", "No explanation"
            )
            explanation_parts.append(
                f"Semantic Analysis (weight {weights['semantic_weight']:.2f}): {semantic_exp}"
            )

        return " | ".join(explanation_parts)


def create_supervisor_agent(config=None) -> LangChainSupervisorAgent:
    return LangChainSupervisorAgent(config)
