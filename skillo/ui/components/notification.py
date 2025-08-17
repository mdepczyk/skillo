"""Streamlit implementation of NotificationService."""

import streamlit as st

from skillo.domain.events.base import BaseEvent, EventHandler
from skillo.domain.interfaces.notification import NotificationService


class StreamlitNotificationHandler(NotificationService, EventHandler):
    """Streamlit-specific implementation of notification service."""

    def show_success(self, message: str) -> None:
        """Display success notification using Streamlit."""
        st.success(f"✅ {message}")

    def show_error(self, message: str) -> None:
        """Display error notification using Streamlit."""
        st.error(f"❌ {message}")

    def show_info(self, message: str) -> None:
        """Display informational notification using Streamlit."""
        st.info(f"ℹ️ {message}")

    def show_warning(self, message: str) -> None:
        """Display warning notification using Streamlit."""
        st.warning(f"⚠️ {message}")

    def handle(self, event: BaseEvent) -> None:
        """Handle domain event by displaying appropriate notification."""
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
