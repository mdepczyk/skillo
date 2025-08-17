from typing import TypedDict

import yaml  # type: ignore
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.infrastructure.adapters import ExperienceAnalysisResponseAdapter
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger
from skillo.infrastructure.tools import (
    calculate_years_between_tool,
    get_current_date_tool,
)

DEFAULT_EXPERIENCE_LEVEL = "Not specified"


class ExperienceAnalysisResult(TypedDict):
    cv_experience_years: str
    required_experience_years: str
    cv_level: str
    required_level: str
    score: float
    explanation: str


class LangChainExperienceAgent:

    AGENT_NAME = "EXPERIENCE AGENT"

    DEFAULT_RESPONSE: ExperienceAnalysisResult = {
        "cv_experience_years": "Not specified",
        "required_experience_years": "Not specified",
        "cv_level": DEFAULT_EXPERIENCE_LEVEL,
        "required_level": DEFAULT_EXPERIENCE_LEVEL,
        "score": 0.0,
        "explanation": "Error in experience analysis",
    }

    def __init__(self, config: Config):
        prompt_template = f"{config.PROMPTS_DIR}/experience_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["experience_analysis"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        )

        self.tools = [get_current_date_tool, calculate_years_between_tool]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.llm_structured = self.llm.with_structured_output(
            ExperienceAnalysisResponseAdapter
        )

    def analyze_experience_match(
        self, cv_content: str, job_content: str
    ) -> ExperienceAnalysisResult:
        logger.info(self.AGENT_NAME, "Starting experience analysis")

        try:
            system_message = SystemMessage(
                content=self.prompt_config["system_message"]
            )
            user_message = HumanMessage(
                content=self.prompt_config["user_message"].format(
                    cv_content=cv_content, job_content=job_content
                )
            )

            messages = [system_message, user_message]

            tool_response = self.llm_with_tools.invoke(messages)

            enhanced_content = str(user_message.content)
            if (
                hasattr(tool_response, "tool_calls")
                and tool_response.tool_calls
            ):
                logger.info(self.AGENT_NAME, "Date calculation tools called")
                for tool_call in tool_response.tool_calls:
                    if tool_call["name"] == "get_current_date_tool":
                        tool_result = get_current_date_tool.invoke({})
                        logger.info(
                            self.AGENT_NAME,
                            "Current date retrieved",
                            str(tool_result),
                        )
                        enhanced_content = enhanced_content + (
                            f"\n\nCurrent date info: {tool_result}"
                        )
                    elif tool_call["name"] == "calculate_years_between_tool":
                        tool_result = calculate_years_between_tool.invoke(
                            tool_call["args"]
                        )
                        logger.info(
                            self.AGENT_NAME,
                            "Years calculated",
                            str(tool_result),
                        )
                        enhanced_content = enhanced_content + (
                            f"\n\nYears calculation: {tool_result}"
                        )

            user_message = HumanMessage(content=enhanced_content)
            structured_messages = [system_message, user_message]

            raw_response = self.llm_structured.invoke(structured_messages)
            adapter: ExperienceAnalysisResponseAdapter = raw_response  # type: ignore
            response = adapter.to_domain()

            result = {
                "cv_experience_years": response.cv_experience_years,
                "required_experience_years": response.required_experience_years,
                "cv_level": response.cv_level,
                "required_level": response.required_level,
                "score": response.score,
                "explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "Analysis completed",
                f"Score: {response.score:.2f}, CV: {response.cv_experience_years} years, Required: {response.required_experience_years}",
            )
            return result  # type: ignore

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return self.DEFAULT_RESPONSE
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return self.DEFAULT_RESPONSE
