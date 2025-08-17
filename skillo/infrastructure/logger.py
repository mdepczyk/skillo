import threading
from datetime import datetime
from enum import Enum
from typing import List, Optional


class LogLevel(Enum):
    """Log levels."""

    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogEntry:
    """Log entry."""

    def __init__(
        self, level: LogLevel, agent: str, action: str, details: str = ""
    ) -> None:
        self.timestamp = datetime.now()
        self.level = level
        self.agent = agent
        self.action = action
        self.details = details


class Logger:
    """Thread-safe logging system."""

    def __init__(self) -> None:
        self._logs: List[LogEntry] = []
        self._max_logs = 100
        self._log_lock = threading.Lock()

    def _add_log(
        self, level: LogLevel, agent: str, action: str, details: str = ""
    ) -> None:
        """Add log entry to collection."""
        log_entry = LogEntry(level, agent, action, details)

        with self._log_lock:
            self._logs.append(log_entry)

            if len(self._logs) > self._max_logs:
                self._logs = self._logs[-self._max_logs:]

    def info(self, agent: str, action: str, details: str = "") -> None:
        """Log info message."""
        self._add_log(LogLevel.INFO, agent, action, details)

    def success(self, agent: str, action: str, details: str = "") -> None:
        """Log success message."""
        self._add_log(LogLevel.SUCCESS, agent, action, details)

    def warning(self, agent: str, action: str, details: str = "") -> None:
        """Log warning message."""
        self._add_log(LogLevel.WARNING, agent, action, details)

    def error(self, agent: str, action: str, details: str = "") -> None:
        """Log error message."""
        self._add_log(LogLevel.ERROR, agent, action, details)

    def get_logs(self, last_n: Optional[int] = None) -> List[LogEntry]:
        """Get log entries."""
        with self._log_lock:
            if last_n:
                return self._logs[-last_n:].copy()
            return self._logs.copy()

    def clear_logs(self) -> None:
        """Clear all log entries."""
        with self._log_lock:
            self._logs.clear()


logger = Logger()
