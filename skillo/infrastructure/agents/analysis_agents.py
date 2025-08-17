from dataclasses import dataclass

from skillo.infrastructure.agents.langchain_education_agent import (
    LangChainEducationAgent,
)
from skillo.infrastructure.agents.langchain_experience_agent import (
    LangChainExperienceAgent,
)
from skillo.infrastructure.agents.langchain_location_agent import (
    LangChainLocationAgent,
)
from skillo.infrastructure.agents.langchain_preferences_agent import (
    LangChainPreferencesAgent,
)
from skillo.infrastructure.agents.langchain_skills_agent import (
    LangChainSkillsAgent,
)


@dataclass
class AnalysisAgents:
    """Bundle of all analysis agents for dependency injection."""

    skills: LangChainSkillsAgent
    location: LangChainLocationAgent
    experience: LangChainExperienceAgent
    preferences: LangChainPreferencesAgent
    education: LangChainEducationAgent
