import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from skillo.enums import LogLevel


class LogEntry:
    """Single log entry data structure."""

    def __init__(
        self, level: LogLevel, agent: str, action: str, details: str = ""
    ):
        self.timestamp = datetime.now()
        self.level = level
        self.agent = agent
        self.action = action
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "agent": self.agent,
            "action": self.action,
            "details": self.details,
        }


class Logger:
    """Thread-safe logging system for backend operations."""

    def __init__(self):
        self._logs: List[LogEntry] = []
        self._max_logs = 100
        self._log_lock = threading.Lock()

    def _add_log(
        self, level: LogLevel, agent: str, action: str, details: str = ""
    ):
        """Add log entry to collection."""
        log_entry = LogEntry(level, agent, action, details)

        with self._log_lock:
            self._logs.append(log_entry)

            if len(self._logs) > self._max_logs:
                self._logs = self._logs[-self._max_logs:]

    def info(self, agent: str, action: str, details: str = ""):
        """Log info message."""
        self._add_log(LogLevel.INFO, agent, action, details)

    def success(self, agent: str, action: str, details: str = ""):
        """Log success message."""
        self._add_log(LogLevel.SUCCESS, agent, action, details)

    def warning(self, agent: str, action: str, details: str = ""):
        """Log warning message."""
        self._add_log(LogLevel.WARNING, agent, action, details)

    def error(self, agent: str, action: str, details: str = ""):
        """Log error message."""
        self._add_log(LogLevel.ERROR, agent, action, details)

    def get_logs(self, last_n: Optional[int] = None) -> List[LogEntry]:
        """Get log entries."""
        with self._log_lock:
            if last_n:
                return self._logs[-last_n:].copy()
            return self._logs.copy()

    def clear_logs(self):
        """Clear all log entries."""
        with self._log_lock:
            self._logs.clear()

    def get_log_count(self) -> int:
        """Get total number of log entries."""
        with self._log_lock:
            return len(self._logs)


logger = Logger()
