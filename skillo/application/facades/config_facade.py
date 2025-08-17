from typing import List, Optional

from skillo.application.dto import (
    ConfigDto,
    LogEntryDto,
)
from skillo.application.protocols import (
    ConfigProtocol,
    ConfigServiceProtocol,
    LoggerServiceProtocol,
)


class ConfigFacade(ConfigProtocol):
    """Configuration and logging facade."""

    def __init__(
        self,
        config_service: ConfigServiceProtocol,
        logger_service: LoggerServiceProtocol,
    ) -> None:
        """Initialize with services."""
        self._config = config_service
        self._logger = logger_service

    def get_config_values(self) -> ConfigDto:
        """Configuration values."""
        return ConfigDto(
            chroma_db_path=self._config.CHROMA_DB_PATH,
            collection_name=self._config.COLLECTION_NAME,
            embedding_model=self._config.EMBEDDING_MODEL,
            min_match_score=self._config.MIN_MATCH_SCORE,
            top_candidates_count=self._config.TOP_CANDIDATES_COUNT,
            agent_weights=self._config.AGENT_WEIGHTS,
        )

    def get_logs(self, last_n: Optional[int] = None) -> List[LogEntryDto]:
        """Application logs."""
        return self._logger.get_logs(last_n)

    def clear_logs(self) -> None:
        """Clears logs."""
        self._logger.clear_logs()
