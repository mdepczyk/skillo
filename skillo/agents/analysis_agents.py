from dataclasses import dataclass, field
from typing import Any

from skillo.agents.langchain_skills_agent import LangChainSkillsAgent
from skillo.agents.langchain_location_agent import LangChainLocationAgent
from skillo.agents.langchain_experience_agent import LangChainExperienceAgent
from skillo.agents.langchain_preferences_agent import LangChainPreferencesAgent


@dataclass
class AnalysisAgents:
    """Bundle of all analysis agents for dependency injection."""
    skills: Any = field(default_factory=LangChainSkillsAgent)
    location: Any = field(default_factory=LangChainLocationAgent)
    experience: Any = field(default_factory=LangChainExperienceAgent)
    preferences: Any = field(default_factory=LangChainPreferencesAgent)
    semantic: Any = None