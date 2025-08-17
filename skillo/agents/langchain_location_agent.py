import os
from typing import Any, Dict

import yaml
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.enums import CommuteFeasibility, RemoteWorkStatus
from skillo.schemas import LocationAnalysisResponse
from skillo.tools import calculate_distance_tool
from skillo.utils.logger import logger


class LangChainLocationAgent:

    AGENT_NAME = "LOCATION AGENT"

    DEFAULT_RESPONSE = {
        "candidate_location": "Not specified",
        "job_location": "Not specified",
        "remote_work": RemoteWorkStatus.NOT_SPECIFIED.value,
        "distance_km": "Not calculated",
        "commute_feasibility": CommuteFeasibility.POOR.value,
        "score": 0.0,
        "explanation": "Error in location analysis",
    }

    def __init__(self):
        prompts_dir = os.getenv("PROMPTS_DIR")
        prompt_template = f"{prompts_dir}/location_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["location_analysis"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        )

        self.tools = [calculate_distance_tool]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.llm_structured = self.llm.with_structured_output(
            LocationAnalysisResponse
        )

    def analyze_location_match(
        self, cv_content: str, job_content: str
    ) -> Dict[str, Any]:
        logger.info(self.AGENT_NAME, "Starting location analysis")

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

            enhanced_content = user_message.content
            if (
                hasattr(tool_response, "tool_calls")
                and tool_response.tool_calls
            ):
                logger.info(
                    self.AGENT_NAME, "Distance calculation tool called"
                )
                for tool_call in tool_response.tool_calls:
                    if tool_call["name"] == "calculate_distance_tool":
                        tool_result = calculate_distance_tool.invoke(
                            tool_call["args"]
                        )
                        logger.info(
                            self.AGENT_NAME,
                            "Distance calculated",
                            str(tool_result),
                        )
                        enhanced_content += (
                            f"\n\nDistance calculation result: {tool_result}"
                        )

            user_message = HumanMessage(content=enhanced_content)
            structured_messages = [system_message, user_message]

            response: LocationAnalysisResponse = self.llm_structured.invoke(
                structured_messages
            )

            result = {
                "candidate_location": response.candidate_location,
                "job_location": response.job_location,
                "remote_work": response.remote_work,
                "distance_km": response.distance_km,
                "commute_feasibility": response.commute_feasibility.value,
                "score": response.score,
                "explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "Analysis completed",
                f"Score: {response.score:.2f}, Distance: {response.distance_km}, Feasibility: {response.commute_feasibility.value}",
            )
            return result

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return self.DEFAULT_RESPONSE
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return self.DEFAULT_RESPONSE


def create_location_agent() -> LangChainLocationAgent:
    return LangChainLocationAgent()
