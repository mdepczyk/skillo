"""Notification service interface for UI communication."""

from abc import ABC, abstractmethod


class NotificationService(ABC):
    """Abstract notification service for UI communication.

    This interface allows Domain/Application layers to request notifications
    without knowing about specific UI implementations (Streamlit, CLI, web, etc.).
    """

    @abstractmethod
    def show_success(self, message: str) -> None:
        """Display success notification.

        Args:
            message: Success message to display
        """
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        """Display error notification.

        Args:
            message: Error message to display
        """
        pass

    @abstractmethod
    def show_info(self, message: str) -> None:
        """Display informational notification.

        Args:
            message: Info message to display
        """
        pass

    @abstractmethod
    def show_warning(self, message: str) -> None:
        """Display warning notification.

        Args:
            message: Warning message to display
        """
        pass
