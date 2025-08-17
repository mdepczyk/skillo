import yaml
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

from skillo.domain.entities import Document
from skillo.domain.entities.routing_decision import RoutingDecision
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger
from skillo.infrastructure.schemas.agent_responses import AgentRoutingResponse


class AgentRouter:
    """
    Intelligent router that decides which analysis agents to invoke.

    Uses LLM to analyze CV-Job pair and determine the most relevant
    agents for analysis, optimizing for both accuracy and efficiency.
    """

    ROUTER_NAME = "AGENT ROUTER"

    AVAILABLE_AGENTS = {
        "skills": "Compare technical skills and requirements",
        "location": "Analyze location compatibility and remote work",
        "experience": "Evaluate experience level alignment",
        "preferences": "Assess cultural and work style fit",
        "education": "Analyze degree requirements and certifications",
    }

    def __init__(self, config: Config):
        """Initialize AgentRouter with LLM configuration."""
        prompt_template = f"{config.PROMPTS_DIR}/router_prompts.yaml"

        with open(prompt_template, "r", encoding="utf-8") as f:
            self.prompt_config = yaml.safe_load(f)["router"]
        self.llm = ChatOpenAI(
            model=self.prompt_config["model"],
            temperature=self.prompt_config["temperature"],
            max_tokens=self.prompt_config["max_tokens"],
        ).with_structured_output(AgentRoutingResponse)

    def decide_agents(
        self, cv_document: Document, job_document: Document
    ) -> RoutingDecision:
        """
        Analyze CV and Job to decide which agents to invoke.

        Args:
            cv_document: Candidate's CV document
            job_document: Job posting document

        Returns:
            RoutingDecision with selected agents and reasoning
        """
        logger.info(
            self.ROUTER_NAME,
            "Analyzing document pair to determine required agents",
        )

        try:
            cv_summary = self._create_document_summary(cv_document, "CV")
            job_summary = self._create_document_summary(job_document, "Job")

            agents_description = "\n".join(
                [
                    f"- {name}: {desc}"
                    for name, desc in self.AVAILABLE_AGENTS.items()
                ]
            )

            user_message = HumanMessage(
                content=self.prompt_config["user_message"].format(
                    available_agents=agents_description,
                    cv_summary=cv_summary,
                    job_summary=job_summary,
                )
            )

            response = self.llm.invoke([user_message])

            valid_agents = [
                agent
                for agent in response.agents
                if agent in self.AVAILABLE_AGENTS
            ]

            if "skills" not in valid_agents:
                valid_agents.insert(0, "skills")
            if "education" not in valid_agents:
                valid_agents.insert(1, "education")

            routing_decision = RoutingDecision(
                agents=valid_agents,
                reasoning=response.reasoning,
                confidence=response.confidence,
                priority=response.priority,
            )

            logger.success(
                self.ROUTER_NAME,
                "Routing decision completed",
                f"Selected agents: {valid_agents}, Confidence: {response.confidence:.2f}",
            )

            return routing_decision

        except Exception as e:
            logger.error(
                self.ROUTER_NAME,
                f"Error in routing decision: {str(e)}",
            )
            return RoutingDecision(
                agents=list(self.AVAILABLE_AGENTS.keys()),
                reasoning="Error occurred, using all agents as fallback",
                confidence=0.0,
                priority="high",
            )

    def _create_document_summary(
        self, document: Document, doc_type: str
    ) -> str:
        """
        Create concise summary of document for routing analysis.

        Args:
            document: Document to summarize
            doc_type: "CV" or "Job" for context

        Returns:
            String summary highlighting key routing-relevant information
        """
        metadata = document.metadata

        summary_parts = [f"{doc_type} Summary:"]

        if doc_type == "CV":
            if metadata.get("name"):
                summary_parts.append(f"Candidate: {metadata['name']}")
            if metadata.get("job_title"):
                summary_parts.append(f"Role: {metadata['job_title']}")
        else:
            if metadata.get("job_title"):
                summary_parts.append(f"Position: {metadata['job_title']}")
            if metadata.get("contact"):
                summary_parts.append(f"Company: {metadata['contact']}")

        location = metadata.get("location")
        remote_status = metadata.get("remote_work_status")
        if location or remote_status:
            location_info = f"Location: {location or 'Not specified'}"
            if remote_status:
                location_info += f", Remote: {remote_status}"
            summary_parts.append(location_info)

        experience = metadata.get("experience")
        experience_level = metadata.get("experience_level")
        if experience or experience_level:
            exp_info = f"Experience: {experience_level or 'Not specified'}"
            if experience and len(experience) < 100:
                exp_info += f" - {experience[:100]}"
            summary_parts.append(exp_info)

        skills = metadata.get("skills")
        if skills:
            if isinstance(skills, list):
                skills_preview = ", ".join(skills[:5])
            else:
                skills_preview = skills[:150] if len(skills) > 150 else skills
            summary_parts.append(f"Key Skills: {skills_preview}")

        education = metadata.get("education")
        if education:
            if isinstance(education, list) and education:
                education_preview = education[0][:100]
            else:
                education_preview = str(education)[:100]
            summary_parts.append(f"Education: {education_preview}")

        preferences = metadata.get("preferences")
        if preferences:
            pref_preview = (
                preferences[:100] if len(preferences) > 100 else preferences
            )
            summary_parts.append(f"Preferences: {pref_preview}")

        return "\n".join(summary_parts)


def create_agent_router(config: Config) -> AgentRouter:
    """Factory function to create AgentRouter instance."""
    return AgentRouter(config)
