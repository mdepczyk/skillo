from unittest.mock import Mock, patch

from skillo.infrastructure.agents.langchain_supervisor_agent import (
    LangChainSupervisorAgent,
)
from skillo.infrastructure.config.settings import Config


def test_supervisor_agent_basic(mock_openai, test_config):
    with patch.dict(
        "os.environ", {"OPENAI_API_KEY": test_config["OPENAI_API_KEY"]}
    ):
        config = Config()

        agent = LangChainSupervisorAgent(config=config)

        mock_cv = Mock()
        mock_cv.content = "Senior Python Developer with Django experience"
        mock_cv.metadata = {"skills": ["Python", "Django"]}

        mock_job = Mock()
        mock_job.content = "Looking for Python Developer with Django"
        mock_job.metadata = {"requirements": ["Python", "Django"]}

        result = agent.analyze_match(mock_cv, mock_job)

        assert "weighted_final_score" in result
        assert result["weighted_final_score"] >= 0.0
        assert result["weighted_final_score"] <= 1.0
        assert "recommendation" in result

        assert mock_openai.chat.completions.create.call_count >= 1
