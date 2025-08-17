import os
from typing import Any, Dict

import yaml
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.enums import WorkStyleMatch
from skillo.schemas import PreferencesAnalysisResponse
from skillo.utils.logger import logger


class LangChainPreferencesAgent:

    AGENT_NAME = "PREFERENCES AGENT"

    DEFAULT_RESPONSE = {
        "cv_preferences": "Not specified",
        "job_culture": "Not specified",
        "work_style_match": WorkStyleMatch.NOT_COMPATIBLE.value,
        "score": 0.0,
        "explanation": "Error in preferences analysis",
    }

    def __init__(self):
        prompts_dir = os.getenv("PROMPTS_DIR")
        prompt_template = f"{prompts_dir}/preferences_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["preferences_analysis"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(PreferencesAnalysisResponse)

    def analyze_preferences_match(
        self, cv_content: str, job_content: str
    ) -> Dict[str, Any]:
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

            response: PreferencesAnalysisResponse = self.llm.invoke(
                formatted_prompt
            )

            result = {
                "cv_preferences": response.cv_preferences,
                "job_culture": response.job_culture,
                "work_style_match": response.work_style_match.value,
                "score": response.score,
                "explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "Preferences analysis completed",
                f"Score: {response.score:.2f}, Match: {response.work_style_match.value}",
            )
            return result

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return self.DEFAULT_RESPONSE
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return self.DEFAULT_RESPONSE


def create_preferences_agent() -> LangChainPreferencesAgent:
    return LangChainPreferencesAgent()
