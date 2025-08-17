from typing import Any, Dict

from langchain_core.tools import tool

from skillo.domain.entities import Document
from skillo.infrastructure.agents.analysis_agents import AnalysisAgents
from skillo.infrastructure.logger import logger

_agents = None


def initialize_agents(agents: AnalysisAgents):
    """Initialize global agents for tool execution."""
    global _agents
    _agents = agents


_content_extractors = {
    "skills": lambda cv, job: (
        f"Skills: {cv.metadata.get('skills', '') or 'Not specified'}",
        f"Required Skills: {job.metadata.get('skills', '') or 'Not specified'}",
    ),
    "location": lambda cv, job: (
        f"Location: {cv.metadata.get('location', 'Not specified')}\nRemote Work: {cv.metadata.get('remote_work_status', 'Not specified')}",
        f"Location: {job.metadata.get('location', 'Not specified')}\nRemote Work: {job.metadata.get('remote_work_status', 'Not specified')}",
    ),
    "experience": lambda cv, job: (
        f"Level: {cv.metadata.get('experience_level', 'Not specified')}\nDetails: {cv.metadata.get('experience', '') or 'Not specified'}",
        f"Required Level: {job.metadata.get('experience_level', 'Not specified')}\nRequirements: {job.metadata.get('experience', '') or 'Not specified'}",
    ),
    "preferences": lambda cv, job: (
        f"Preferences: {cv.metadata.get('preferences', '') or 'Not specified'}",
        f"Culture: {job.metadata.get('preferences', '') or 'Not specified'}",
    ),
    "education": lambda cv, job: (
        f"Education: {cv.metadata.get('education', '') or 'Not specified'}",
        f"Required Education: {job.metadata.get('education', '') or 'Not specified'}",
    ),
}

_agent_executors = {
    "skills": lambda cv_content, job_content: _agents.skills.analyze_skills_match(
        cv_content, job_content
    ),
    "location": lambda cv_content, job_content: _agents.location.analyze_location_match(
        cv_content, job_content
    ),
    "experience": lambda cv_content, job_content: _agents.experience.analyze_experience_match(
        cv_content, job_content
    ),
    "preferences": lambda cv_content, job_content: _agents.preferences.analyze_preferences_match(
        cv_content, job_content
    ),
    "education": lambda cv_content, job_content: _agents.education.analyze_education_match(
        cv_content, job_content
    ),
}


@tool
def run_agent_analysis(
    agent_name: str, cv_document: Document, job_document: Document
) -> Dict[str, Any]:
    """
    Execute a specific analysis agent on CV-Job document pair.

    Simple, narrowly-scoped tool that runs one agent and returns structured results.
    Follows LangChain best practices for tool design.

    Args:
        agent_name: Name of agent to run (skills, location, experience, preferences, education)
        cv_document: Candidate's CV document with metadata
        job_document: Job posting document with metadata

    Returns:
        Dict containing agent analysis results with score and explanation

    Raises:
        ValueError: If agent_name is not supported
        Exception: If agent execution fails
    """
    if _agents is None:
        raise RuntimeError("Agents not initialized. Call initialize_agents() first.")

    if agent_name not in _agent_executors:
        available_agents = ", ".join(_agent_executors.keys())
        raise ValueError(
            f"Unknown agent '{agent_name}'. Available: {available_agents}"
        )

    try:
        logger.info(
            "AGENT_TOOL", f"Executing {agent_name.upper()} agent analysis"
        )

        cv_content, job_content = _content_extractors[agent_name](
            cv_document, job_document
        )

        result = _agent_executors[agent_name](cv_content, job_content)

        logger.success(
            "AGENT_TOOL",
            f"{agent_name.upper()} analysis completed",
            f"Score: {result.get('score', 0.0):.3f}",
        )

        return result

    except Exception as e:
        error_msg = f"Failed to execute {agent_name} agent: {str(e)}"
        logger.error("AGENT_TOOL", error_msg)

        return {
            "score": 0.0,
            "explanation": f"Error in {agent_name} analysis: {str(e)}",
            "error": True,
        }


def get_available_agents() -> list[str]:
    """Get list of available agent names for this tool."""
    return list(_agent_executors.keys())


def validate_documents(cv_document: Document, job_document: Document) -> bool:
    """Validate that documents have required structure."""
    return (
        hasattr(cv_document, "metadata")
        and hasattr(job_document, "metadata")
        and isinstance(cv_document.metadata, dict)
        and isinstance(job_document.metadata, dict)
    )
