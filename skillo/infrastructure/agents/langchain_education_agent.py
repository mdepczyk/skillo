from typing import TypedDict

import yaml  # type: ignore
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.infrastructure.adapters import EducationAnalysisResponseAdapter
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger

DEFAULT_EDUCATION_LEVEL = "Not specified"
DEFAULT_EDUCATION_MATCH = "Below Requirements"


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
    """Education Agent for analyzing educational background compatibility between candidates and jobs."""

    AGENT_NAME = "EDUCATION AGENT"

    DEFAULT_RESPONSE: EducationAnalysisResult = {
        "cv_degree": DEFAULT_EDUCATION_LEVEL,
        "cv_field": "Not specified",
        "required_degree": DEFAULT_EDUCATION_LEVEL,
        "required_field": "Not specified",
        "certifications": "None mentioned",
        "degree_match": DEFAULT_EDUCATION_MATCH,
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
        ).with_structured_output(EducationAnalysisResponseAdapter)

    def analyze_education_match(
        self, cv_content: str, job_content: str
    ) -> EducationAnalysisResult:
        """Analyze educational background compatibility between CV and job."""
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

            raw_response = self.llm.invoke([system_message, user_message])
            adapter: EducationAnalysisResponseAdapter = raw_response  # type: ignore
            response = adapter.to_domain()

            result = {
                "cv_degree": response.cv_degree,
                "cv_field": response.cv_field,
                "required_degree": response.required_degree,
                "required_field": response.required_field,
                "certifications": response.certifications,
                "degree_match": response.degree_match,
                "score": response.score,
                "explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "Education analysis completed",
                f"Score: {response.score:.3f}, Match: {response.degree_match}",
            )

            return result  # type: ignore

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
