import os
from typing import Any, Dict

import yaml
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.schemas import DocumentProcessingResponse
from skillo.utils.logger import logger


class LangChainJobProcessingAgent:

    AGENT_NAME = "JOB PROCESSING AGENT"

    DEFAULT_JOB_RESPONSE = {
        "document_type": "job",
        "job_title": "Not specified",
        "company": "Not specified",
        "required_skills": [],
        "experience_requirements": [],
        "education_requirements": [],
        "location": "Not specified",
        "culture_preferences": [],
    }

    def __init__(self):
        prompts_dir = os.getenv("PROMPTS_DIR")
        prompt_template = f"{prompts_dir}/job_processing_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["job_processing"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(DocumentProcessingResponse)

    def process_job_posting(self, job_content: str) -> Dict[str, Any]:
        logger.info(self.AGENT_NAME, "Starting job posting processing")

        try:
            formatted_user_message = self.prompt_config["user_message"].format(
                document_content=job_content
            )

            messages = [
                ("system", self.prompt_config["system_message"]),
                ("human", formatted_user_message),
            ]

            response: DocumentProcessingResponse = self.llm.invoke(messages)

            sections = {
                "job_title": response.name,
                "company": response.contact,
                "required_skills": response.skills,
                "experience_requirements": response.experience,
                "education_requirements": response.education,
                "location": response.location,
                "culture_preferences": response.preferences,
            }

            result = {
                "document_type": "job",
                "sections": sections,
            }

            logger.success(
                self.AGENT_NAME,
                "Job processing completed",
                f"Title: {response.name}, Skills: {len(response.skills)}, Experience: {len(response.experience)}",
            )
            return result

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return self.DEFAULT_JOB_RESPONSE
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return self.DEFAULT_JOB_RESPONSE


def create_job_processing_agent() -> LangChainJobProcessingAgent:
    return LangChainJobProcessingAgent()
