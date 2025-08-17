from unittest.mock import patch

from skillo.infrastructure.config.settings import Config


def test_application_starts_with_valid_config(test_config):
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": test_config["OPENAI_API_KEY"],
            "CHROMA_DB_PATH": test_config["CHROMA_DB_PATH"],
            "COLLECTION_NAME": test_config["COLLECTION_NAME"],
        },
    ):
        config = Config()

        assert config.OPENAI_API_KEY is not None
        assert len(config.OPENAI_API_KEY) > 0
        assert config.CHROMA_DB_PATH is not None
        assert config.COLLECTION_NAME is not None
        assert config.MIN_MATCH_SCORE >= 0.0
        assert config.TOP_CANDIDATES_COUNT > 0

        weights_sum = sum(config.AGENT_WEIGHTS.values())
        assert abs(weights_sum - 1.0) < 0.01
