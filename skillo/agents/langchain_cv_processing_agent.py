import os
from typing import Any, Dict

import yaml
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.schemas import DocumentProcessingResponse
from skillo.tools.profile_classifier import get_profile_classifier
from skillo.utils.logger import logger


class LangChainCVProcessingAgent:

    AGENT_NAME = "CV PROCESSING AGENT"

    DEFAULT_CV_RESPONSE = {
        "document_type": "cv",
        "name": "Not specified",
        "contact": "Not specified",
        "skills": [],
        "experience": [],
        "education": [],
        "location": "Not specified",
        "preferences": [],
        "profile": "Unknown",
    }

    def __init__(self):
        prompts_dir = os.getenv("PROMPTS_DIR")
        prompt_template = f"{prompts_dir}/cv_processing_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["cv_processing"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(DocumentProcessingResponse)

    def process_cv(self, cv_content: str) -> Dict[str, Any]:
        logger.info(self.AGENT_NAME, "Starting CV processing")

        try:
            user_message = self.prompt_config["user_message"].format(
                document_content=cv_content
            )

            messages = [
                ("system", self.prompt_config["system_message"]),
                ("human", user_message),
            ]

            response: DocumentProcessingResponse = self.llm.invoke(messages)

            profile_classifier = get_profile_classifier()
            profile = profile_classifier.classify_profile(cv_content)

            sections = {
                "personal_information": {"name": response.name, "contact": response.contact},
                "skills": response.skills,
                "experience": response.experience,
                "education": response.education,
                "location": response.location,
                "preferences": response.preferences,
            }

            result = {
                "document_type": "cv",
                "profile": profile,
                "sections": sections,
            }

            logger.success(
                self.AGENT_NAME,
                "CV processing completed",
                f"Profile: {profile}, Skills: {len(response.skills)}, Experience: {len(response.experience)}",
            )
            return result

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return self.DEFAULT_CV_RESPONSE
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return self.DEFAULT_CV_RESPONSE


def create_cv_processing_agent() -> LangChainCVProcessingAgent:
    return LangChainCVProcessingAgent()
