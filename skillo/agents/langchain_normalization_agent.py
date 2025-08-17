import os
from typing import Any, Dict

import yaml
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.enums import ExperienceLevel, RemoteWorkStatus
from skillo.schemas import NormalizationResponse
from skillo.utils.logger import logger


class LangChainNormalizationAgent:

    AGENT_NAME = "NORMALIZATION AGENT"

    DEFAULT_CV_RESPONSE = {
        "normalized_job_title": "Not specified",
        "normalized_location": "Not specified",
        "normalized_skills": [],
        "remote_work_status": RemoteWorkStatus.NOT_SPECIFIED.value,
        "experience_level": ExperienceLevel.NOT_SPECIFIED.value,
        "industry_sector": "Not specified",
        "normalization_explanation": "Error in CV normalization",
    }

    DEFAULT_JOB_RESPONSE = {
        "normalized_job_title": "Not specified",
        "normalized_location": "Not specified",
        "normalized_skills": [],
        "remote_work_status": RemoteWorkStatus.NOT_SPECIFIED.value,
        "experience_level": ExperienceLevel.NOT_SPECIFIED.value,
        "industry_sector": "Not specified",
        "normalization_explanation": "Error in job normalization",
    }

    def __init__(self):
        prompts_dir = os.getenv("PROMPTS_DIR")
        prompt_template = f"{prompts_dir}/normalization_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["normalization"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(NormalizationResponse)

    def normalize_cv_data(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(self.AGENT_NAME, "Starting CV data normalization")

        try:
            sections = cv_data.get("sections", {})
            
            personal_info = sections.get("personal_information", {})
            name = personal_info.get("name", "Not specified")
            skills = sections.get("skills", [])
            experience = sections.get("experience", [])
            location = sections.get("location", "Not specified")
            preferences = sections.get("preferences", [])

            user_message = self.prompt_config["cv_user_message"].format(
                name=name,
                skills=", ".join(skills) if skills else "Not specified",
                experience="; ".join(experience) if experience else "Not specified",
                location=location,
                preferences="; ".join(preferences) if preferences else "Not specified",
            )

            messages = [
                ("system", self.prompt_config["cv_system_message"]),
                ("human", user_message),
            ]

            response: NormalizationResponse = self.llm.invoke(messages)

            normalized_sections = sections.copy()
            normalized_sections["skills"] = response.normalized_skills
            normalized_sections["location"] = response.normalized_location

            result = {
                "document_type": cv_data.get("document_type"),
                "profile": cv_data.get("profile"),
                "sections": normalized_sections,
                "normalized_job_title": response.normalized_job_title,
                "normalized_location": response.normalized_location,
                "normalized_skills": response.normalized_skills,
                "remote_work_status": response.remote_work_status.value,
                "experience_level": response.experience_level.value,
                "industry_sector": response.industry_sector,
                "normalization_explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "CV normalization completed",
                f"Title: {response.normalized_job_title}, Skills: {len(response.normalized_skills)}",
            )
            return result

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return {**cv_data, **self.DEFAULT_CV_RESPONSE}
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return {**cv_data, **self.DEFAULT_CV_RESPONSE}

    def normalize_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(self.AGENT_NAME, "Starting job data normalization")

        try:
            sections = job_data.get("sections", {})
            
            job_title = sections.get("job_title", "Not specified")
            required_skills = sections.get("required_skills", [])
            experience_requirements = sections.get("experience_requirements", [])
            location = sections.get("location", "Not specified")
            culture_preferences = sections.get("culture_preferences", [])

            formatted_user_message = self.prompt_config[
                "job_user_message"
            ].format(
                job_title=job_title,
                required_skills=", ".join(required_skills) if required_skills else "Not specified",
                experience_requirements="; ".join(experience_requirements) if experience_requirements else "Not specified",
                location=location,
                culture_preferences="; ".join(culture_preferences) if culture_preferences else "Not specified",
            )

            messages = [
                ("system", self.prompt_config["job_system_message"]),
                ("human", formatted_user_message),
            ]

            response: NormalizationResponse = self.llm.invoke(messages)

            normalized_sections = sections.copy()
            normalized_sections["job_title"] = response.normalized_job_title
            normalized_sections["required_skills"] = response.normalized_skills
            normalized_sections["location"] = response.normalized_location

            result = {
                "document_type": job_data.get("document_type"),
                "sections": normalized_sections,
                "normalized_job_title": response.normalized_job_title,
                "normalized_location": response.normalized_location,
                "normalized_skills": response.normalized_skills,
                "remote_work_status": response.remote_work_status.value,
                "experience_level": response.experience_level.value,
                "industry_sector": response.industry_sector,
                "normalization_explanation": response.explanation,
            }

            logger.success(
                self.AGENT_NAME,
                "Job normalization completed",
                f"Title: {response.normalized_job_title}, Skills: {len(response.normalized_skills)}",
            )
            return result

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return {**job_data, **self.DEFAULT_JOB_RESPONSE}
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return {**job_data, **self.DEFAULT_JOB_RESPONSE}


def create_normalization_agent() -> LangChainNormalizationAgent:
    return LangChainNormalizationAgent()
