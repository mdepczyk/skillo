from typing import TypedDict

import yaml
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.domain.enums import EducationLevel, EducationMatch
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger
from skillo.infrastructure.schemas import EducationAnalysisResponse


class EducationAnalysisResult(TypedDict):
    cv_degree: str
    cv_field: str
    required_degree: str
    required_field: str
    certifications: str
    degree_match: str
    score: float
    explanation: str


class LangChainEducationAgent:
    """
    Education Agent for analyzing educational background compatibility.

    Evaluates degree levels, field alignment, certifications, and overall
    educational fit between candidate and job requirements.
    """

    AGENT_NAME = "EDUCATION AGENT"

    DEFAULT_RESPONSE: EducationAnalysisResult = {
        "cv_degree": EducationLevel.NOT_SPECIFIED.value,
        "cv_field": "Not specified",
        "required_degree": EducationLevel.NOT_SPECIFIED.value,
        "required_field": "Not specified",
        "certifications": "None mentioned",
        "degree_match": EducationMatch.BELOW_REQUIREMENTS.value,
        "score": 0.0,
        "explanation": "Error in education analysis",
    }

    def __init__(self, config: Config):
        """Initialize Education Agent with prompts and LLM configuration."""
        prompt_template = f"{config.PROMPTS_DIR}/education_prompts.yaml"

        try:
            with open(prompt_template, "r", encoding="utf-8") as f:
                self.prompt_config = yaml.safe_load(f)["education_analysis"]
        except FileNotFoundError:
            logger.error(
                self.AGENT_NAME,
                f"Prompt template not found: {prompt_template}",
            )
            raise
        except KeyError:
            logger.error(
                self.AGENT_NAME,
                "Invalid prompt configuration structure",
            )
            raise

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(EducationAnalysisResponse)

    def analyze_education_match(
        self, cv_content: str, job_content: str
    ) -> EducationAnalysisResult:
        """
        Analyze educational background compatibility between CV and job.

        Args:
            cv_content: Education section content from CV
            job_content: Education requirements from job posting

        Returns:
            Dict containing education analysis results with score and explanation
        """
        logger.info(
            self.AGENT_NAME,
            "Starting education analysis for CV vs Job requirements",
        )

        try:
            system_message = SystemMessage(
                content=self.prompt_config["system_message"]
            )

            user_message = HumanMessage(
                content=self.prompt_config["user_message"].format(
                    cv_content=cv_content,
                    job_content=job_content,
                )
            )

            response = self.llm.invoke([system_message, user_message])

            result = {
                "cv_degree": response.cv_degree.value,
                "cv_field": response.cv_field,
                "required_degree": response.required_degree.value,
                "required_field": response.required_field,
                "certifications": response.certifications,
                "degree_match": response.degree_match.value,
                "score": response.score,
                "explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "Education analysis completed",
                f"Score: {response.score:.3f}, Match: {response.degree_match.value}",
            )

            return result

        except ValidationError as e:
            logger.error(
                self.AGENT_NAME,
                f"Response validation error: {e}",
            )
            return self.DEFAULT_RESPONSE

        except Exception as e:
            logger.error(
                self.AGENT_NAME,
                f"Unexpected error in education analysis: {str(e)}",
            )
            return self.DEFAULT_RESPONSE


def create_education_agent(config: Config) -> LangChainEducationAgent:
    """Factory function to create Education Agent instance."""
    return LangChainEducationAgent(config)
