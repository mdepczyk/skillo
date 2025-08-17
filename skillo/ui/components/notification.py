import streamlit as st

from skillo.application.dto import EventDto
from skillo.application.protocols import EventHandler, NotificationService


class StreamlitNotificationHandler(NotificationService, EventHandler):
    """Streamlit notification handler."""

    def show_success(self, message: str) -> None:
        """Success notification."""
        st.success(f"✅ {message}")

    def show_error(self, message: str) -> None:
        """Error notification."""
        st.error(f"❌ {message}")

    def show_info(self, message: str) -> None:
        """Info notification."""
        st.info(f"ℹ️ {message}")

    def show_warning(self, message: str) -> None:
        """Warning notification."""
        st.warning(f"⚠️ {message}")

    def handle(self, event: EventDto) -> None:
        """Event handler."""
        if event.level == "success":
            self.show_success(event.message)
        elif event.level == "error":
            self.show_error(event.message)
        elif event.level == "warning":
            self.show_warning(event.message)
        elif event.level == "info":
            self.show_info(event.message)
        else:
            self.show_info(f"{event.event_type}: {event.message}")
