import yaml  # type: ignore
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.domain.schemas import (
    DocumentProcessingResponse,
    NormalizationResponse,
)
from skillo.infrastructure.adapters import NormalizationResponseAdapter
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger


class LangChainNormalizationAgent:

    AGENT_NAME = "NORMALIZATION AGENT"

    def __init__(self, config: Config):
        prompt_template = f"{config.PROMPTS_DIR}/normalization_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["normalization"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(NormalizationResponseAdapter)

    def normalize_cv_data(
        self, cv_response: DocumentProcessingResponse
    ) -> NormalizationResponse:
        logger.info(self.AGENT_NAME, "Starting CV data normalization")

        try:
            user_message = self.prompt_config["cv_user_message"].format(
                name=cv_response.name,
                skills=(
                    ", ".join(cv_response.skills)
                    if cv_response.skills
                    else "Not specified"
                ),
                experience=(
                    "; ".join(cv_response.experience)
                    if cv_response.experience
                    else "Not specified"
                ),
                location=cv_response.location,
                preferences=(
                    "; ".join(cv_response.preferences)
                    if cv_response.preferences
                    else "Not specified"
                ),
            )

            messages = [
                ("system", self.prompt_config["cv_system_message"]),
                ("human", user_message),
            ]

            raw_response = self.llm.invoke(messages)
            adapter: NormalizationResponseAdapter = raw_response  # type: ignore
            response = adapter.to_domain()

            logger.success(
                self.AGENT_NAME,
                "CV normalization completed",
                f"Title: {response.normalized_job_title}, Skills: {len(response.normalized_skills)}",
            )
            return response

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            raise

        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            raise

    def normalize_job_data(
        self, job_response: DocumentProcessingResponse
    ) -> NormalizationResponse:
        logger.info(self.AGENT_NAME, "Starting job data normalization")

        try:
            formatted_user_message = self.prompt_config[
                "job_user_message"
            ].format(
                job_title=job_response.name,
                required_skills=(
                    ", ".join(job_response.skills)
                    if job_response.skills
                    else "Not specified"
                ),
                experience_requirements=(
                    "; ".join(job_response.experience)
                    if job_response.experience
                    else "Not specified"
                ),
                location=job_response.location,
                culture_preferences=(
                    "; ".join(job_response.preferences)
                    if job_response.preferences
                    else "Not specified"
                ),
            )

            messages = [
                ("system", self.prompt_config["job_system_message"]),
                ("human", formatted_user_message),
            ]

            raw_response = self.llm.invoke(messages)
            adapter: NormalizationResponseAdapter = raw_response  # type: ignore
            response = adapter.to_domain()

            logger.success(
                self.AGENT_NAME,
                "Job normalization completed",
                f"Title: {response.normalized_job_title}, Skills: {len(response.normalized_skills)}",
            )
            return response

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            raise

        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            raise
