import os
from typing import Any, Dict

import yaml
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.enums import ContextualFit, IndustryAlignment
from skillo.schemas import SemanticAnalysisResponse
from skillo.utils.logger import logger


class LangChainSemanticAgent:

    AGENT_NAME = "SEMANTIC AGENT"

    DEFAULT_RESPONSE = {
        "embedding_similarity": 0.0,
        "contextual_fit": ContextualFit.POOR.value,
        "industry_alignment": IndustryAlignment.LOW.value,
        "score": 0.0,
        "explanation": "Error in semantic analysis",
    }

    def __init__(self, vectorstore=None):
        prompts_dir = os.getenv("PROMPTS_DIR")
        prompt_template = f"{prompts_dir}/semantic_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["semantic_analysis"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(SemanticAnalysisResponse)

        self.vectorstore = vectorstore

    def analyze_semantic_similarity(
        self, cv_sections: Dict[str, str], job_sections: Dict[str, str]
    ) -> Dict[str, Any]:
        logger.info(
            self.AGENT_NAME, "Starting semantic analysis with chunked sections"
        )

        try:
            section_similarities = self._calculate_section_similarities(
                cv_sections, job_sections
            )

            overall_similarity = self._calculate_overall_similarity(
                section_similarities
            )

            logger.info(
                self.AGENT_NAME,
                "Section similarities calculated",
                f"Overall: {overall_similarity:.3f}, Details: {section_similarities}",
            )

            cv_summary = self._create_section_summary(cv_sections)
            job_summary = self._create_section_summary(job_sections)

            system_message = SystemMessage(
                content=self.prompt_config["system_message"]
            )
            user_message = HumanMessage(
                content=self.prompt_config["user_message"].format(
                    cv_content=cv_summary,
                    job_content=job_summary,
                    similarity=overall_similarity,
                )
            )

            formatted_prompt = [system_message, user_message]

            response: SemanticAnalysisResponse = self.llm.invoke(
                formatted_prompt
            )

            result = {
                "embedding_similarity": overall_similarity,
                "contextual_fit": response.contextual_fit.value,
                "industry_alignment": response.industry_alignment.value,
                "score": overall_similarity,
                "explanation": f"Section-wise analysis: {section_similarities}. {response.explanation}",
                "section_similarities": section_similarities,
            }

            logger.success(
                self.AGENT_NAME,
                "Analysis completed",
                f"Score: {overall_similarity:.3f}, Contextual: {response.contextual_fit.value}, Industry: {response.industry_alignment.value}",
            )
            return result

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            return self.DEFAULT_RESPONSE
        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            return self.DEFAULT_RESPONSE

    def _calculate_section_similarities(
        self, cv_sections: Dict[str, str], job_sections: Dict[str, str]
    ) -> Dict[str, float]:
        similarities = {}

        key_sections = ["skills", "experience"]

        section_mapping = {
            "skills": "required_skills",
            "experience": "experience_requirements",
        }

        for cv_section in key_sections:
            job_section = section_mapping.get(cv_section, cv_section)
            cv_content = cv_sections.get(cv_section, "").strip()
            job_content = job_sections.get(job_section, "").strip()

            if cv_content and job_content and self.vectorstore:
                try:
                    similarity = (
                        self.vectorstore.calculate_semantic_similarity(
                            cv_content, job_content
                        )
                    )
                    similarities[cv_section] = similarity
                except Exception as e:
                    logger.error(
                        self.AGENT_NAME,
                        f"Error calculating {cv_section} similarity",
                        str(e),
                    )
                    similarities[cv_section] = 0.0
            else:
                similarities[cv_section] = (
                    0.0 if not cv_content or not job_content else 0.5
                )

        return similarities

    def _calculate_overall_similarity(
        self, section_similarities: Dict[str, float]
    ) -> float:
        weights = {"skills": 0.60, "experience": 0.40}

        total_weight = 0.0
        weighted_sum = 0.0

        for section, similarity in section_similarities.items():
            if section in weights:
                weight = weights[section]
                weighted_sum += similarity * weight
                total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _create_section_summary(self, sections: Dict[str, str]) -> str:
        summary_parts = []

        for section_name, content in sections.items():
            if content.strip():
                summary_parts.append(f"{section_name}: {content}")

        return "\n".join(summary_parts)


def create_semantic_agent(vectorstore=None) -> LangChainSemanticAgent:
    return LangChainSemanticAgent(vectorstore=vectorstore)
