import yaml
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger
from skillo.infrastructure.schemas import DocumentProcessingResponse
from skillo.infrastructure.tools.profile_classifier import ProfileClassifier


class LangChainCVProcessingAgent:

    AGENT_NAME = "CV PROCESSING AGENT"

    def __init__(self, profile_classifier: ProfileClassifier, config: Config):
        self._profile_classifier = profile_classifier

        prompt_template = f"{config.PROMPTS_DIR}/cv_processing_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["cv_processing"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(DocumentProcessingResponse)

    def process_cv(
        self, cv_content: str
    ) -> tuple[DocumentProcessingResponse, str]:
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

            profile = self._profile_classifier.classify_profile(cv_content)

            logger.success(
                self.AGENT_NAME,
                "CV processing completed",
                f"Profile: {profile}, Skills: {len(response.skills)}, Experience: {len(response.experience)}",
            )
            return response, profile

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            raise

        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            raise


def create_cv_processing_agent(profile_classifier: ProfileClassifier, config: Config) -> LangChainCVProcessingAgent:
    return LangChainCVProcessingAgent(profile_classifier, config)
