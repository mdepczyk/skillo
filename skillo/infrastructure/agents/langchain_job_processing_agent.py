import yaml  # type: ignore
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from skillo.domain.schemas import DocumentProcessingResponse
from skillo.infrastructure.adapters import DocumentProcessingResponseAdapter
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger


class LangChainJobProcessingAgent:

    AGENT_NAME = "JOB PROCESSING AGENT"

    def __init__(self, config: Config):
        prompt_template = f"{config.PROMPTS_DIR}/job_processing_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["job_processing"]

        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(DocumentProcessingResponseAdapter)

    def process_document(self, content: str) -> DocumentProcessingResponse:
        logger.info(self.AGENT_NAME, "Starting job posting processing")

        try:
            formatted_user_message = self.prompt_config["user_message"].format(
                document_content=content
            )

            messages = [
                ("system", self.prompt_config["system_message"]),
                ("human", formatted_user_message),
            ]

            raw_response = self.llm.invoke(messages)
            adapter: DocumentProcessingResponseAdapter = raw_response  # type: ignore
            response = adapter.to_domain()

            logger.success(
                self.AGENT_NAME,
                "Job processing completed",
                f"Title: {response.name}, Skills: {len(response.skills)}, Experience: {len(response.experience)}",
            )
            return response

        except ValidationError as e:
            logger.error(self.AGENT_NAME, "Validation error", str(e))
            raise

        except Exception as e:
            logger.error(self.AGENT_NAME, "Unexpected error", str(e))
            raise
