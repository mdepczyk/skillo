import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "skillo")

    CV_UPLOAD_DIR: str = os.getenv("CV_UPLOAD_DIR", "./data/cvs")
    JOB_UPLOAD_DIR: str = os.getenv("JOB_UPLOAD_DIR", "./data/jobs")
    PROMPTS_DIR: str = os.getenv("PROMPTS_DIR", "./skillo/prompts")

    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "text-embedding-ada-002"
    )

    MIN_MATCH_SCORE: float = float(os.getenv("MIN_MATCH_SCORE", "0.3"))
    TOP_CANDIDATES_COUNT: int = int(os.getenv("TOP_CANDIDATES_COUNT", "5"))

    @property
    def AGENT_WEIGHTS(self) -> Dict[str, float]:
        """Get agent weights from environment or defaults."""
        return {
            "location": float(os.getenv("LOCATION_WEIGHT", "0.15")),
            "skills": float(os.getenv("SKILLS_WEIGHT", "0.30")),
            "experience": float(os.getenv("EXPERIENCE_WEIGHT", "0.25")),
            "preferences": float(os.getenv("PREFERENCES_WEIGHT", "0.10")),
            "semantic": float(os.getenv("SEMANTIC_WEIGHT", "0.20")),
        }

    def validate_weights(self) -> bool:
        """Validate that agent weights sum to 1.0."""
        total = sum(self.AGENT_WEIGHTS.values())
        return abs(total - 1.0) < 0.01

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "openai_api_key": "***" if self.OPENAI_API_KEY else None,
            "chroma_db_path": self.CHROMA_DB_PATH,
            "collection_name": self.COLLECTION_NAME,
            "embedding_model": self.EMBEDDING_MODEL,
            "min_match_score": self.MIN_MATCH_SCORE,
            "top_candidates_count": self.TOP_CANDIDATES_COUNT,
            "agent_weights": self.AGENT_WEIGHTS,
        }


def validate_config(config: Config = None) -> bool:
    """
    Validate that all required configuration is present and valid.

    Args:
        config: Config instance to validate (uses default if None)

    Returns:
        bool: True if configuration is valid

    Raises:
        ValueError: If configuration is invalid
    """
    if config is None:
        config = Config()

    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    if not config.validate_weights():
        weights = config.AGENT_WEIGHTS
        total = sum(weights.values())
        raise ValueError(
            f"Agent weights must sum to 1.0, got {total:.3f}. "
            f"Current weights: {weights}"
        )

    if config.MIN_MATCH_SCORE < 0 or config.MIN_MATCH_SCORE > 1:
        raise ValueError("MIN_MATCH_SCORE must be between 0 and 1")

    if config.TOP_CANDIDATES_COUNT < 1:
        raise ValueError("TOP_CANDIDATES_COUNT must be at least 1")

    return True
