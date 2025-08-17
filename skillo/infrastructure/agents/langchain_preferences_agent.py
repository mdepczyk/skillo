from typing import TypedDict

import yaml  # type: ignore
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.infrastructure.adapters import PreferencesAnalysisResponseAdapter
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger

DEFAULT_WORK_STYLE_MATCH = "Not Compatible"


class PreferencesAnalysisResult(TypedDict):
    cv_preferences: str
    job_culture: str
    work_style_match: str
    score: float
    explanation: str


class LangChainPreferencesAgent:

    AGENT_NAME = "PREFERENCES AGENT"

    DEFAULT_RESPONSE: PreferencesAnalysisResult = {
        "cv_preferences": "Not specified",
        "job_culture": "Not specified",
        "work_style_match": DEFAULT_WORK_STYLE_MATCH,
        "score": 0.0,
        "explanation": "Error in preferences analysis",
    }

    def __init__(self, config: Config):
        prompt_template = f"{config.PROMPTS_DIR}/preferences_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["preferences_analysis"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(PreferencesAnalysisResponseAdapter)

    def analyze_preferences_match(
        self, cv_content: str, job_content: str
    ) -> PreferencesAnalysisResult:
        logger.info(self.AGENT_NAME, "Starting preferences analysis")

        try:
            system_message = SystemMessage(
                content=self.prompt_config["system_message"]
            )
            user_message = HumanMessage(
                content=self.prompt_config["user_message"].format(
                    cv_content=cv_content, job_content=job_content
                )
            )

            formatted_prompt = [system_message, user_message]

            raw_response = self.llm.invoke(formatted_prompt)
            adapter: PreferencesAnalysisResponseAdapter = raw_response  # type: ignore
            response = adapter.to_domain()

            result = {
                "cv_preferences": response.cv_preferences,
                "job_culture": response.job_culture,
                "work_style_match": response.work_style_match,
                "score": response.score,
                "explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "Preferences analysis completed",
                f"Score: {response.score:.2f}, Match: {response.work_style_match}",
            )
            return result  # type: ignore

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return self.DEFAULT_RESPONSE
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return self.DEFAULT_RESPONSE
