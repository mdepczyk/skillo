from typing import List, TypedDict

import yaml  # type: ignore
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.infrastructure.adapters import SkillsAnalysisResponseAdapter
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger


class SkillsAnalysisResult(TypedDict):
    cv_skills: List[str]
    required_skills: List[str]
    matched_skills: List[str]
    score: float
    explanation: str


class LangChainSkillsAgent:

    AGENT_NAME = "SKILLS AGENT"

    DEFAULT_RESPONSE: SkillsAnalysisResult = {
        "cv_skills": [],
        "required_skills": [],
        "matched_skills": [],
        "score": 0.0,
        "explanation": "Error in skills analysis",
    }

    def __init__(self, config: Config) -> None:
        prompt_template = f"{config.PROMPTS_DIR}/skills_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["skills_analysis"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(SkillsAnalysisResponseAdapter)

    def analyze_skills_match(
        self, cv_content: str, job_content: str
    ) -> SkillsAnalysisResult:
        logger.info(self.AGENT_NAME, "Starting skills analysis")

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
            adapter: SkillsAnalysisResponseAdapter = raw_response  # type: ignore
            response = adapter.to_domain()

            result: SkillsAnalysisResult = {
                "cv_skills": response.cv_skills,
                "required_skills": response.required_skills,
                "matched_skills": response.matched_skills,
                "score": response.score,
                "explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "Skills analysis completed",
                f"Score: {response.score:.2f}, Matched skills: {len(response.matched_skills)}",
            )
            return result

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return self.DEFAULT_RESPONSE
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return self.DEFAULT_RESPONSE
