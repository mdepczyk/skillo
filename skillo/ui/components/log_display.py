"""
UI component for displaying logs in Streamlit interface.
"""

from typing import List
import streamlit as st

from skillo.utils.logger import logger, LogEntry
from skillo.enums import LogLevel


def display_logs_section(
    title: str = "🔍 Analysis Logs", show_clear: bool = True
):
    """
    Display logs section in Streamlit interface.

    Args:
        title: Section title
        show_clear: Whether to show clear logs button
    """
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(title)

    with col2:
        if show_clear and st.button("🗑️ Clear Logs", key="clear_logs_btn"):
            logger.clear_logs()
            st.rerun()

    logs = logger.get_logs()
    _render_logs(logs)


def _render_logs(logs: List[LogEntry]):
    """Render log entries in Streamlit."""
    if not logs:
        st.info("No logs available.")
        return

    log_text = _format_logs_as_markdown(logs)

    with st.expander(f"Recent Logs ({len(logs)} total)", expanded=True):
        st.markdown(log_text)


def _format_logs_as_markdown(logs: List[LogEntry]) -> str:
    """Format log entries as markdown text."""
    log_lines = []

    for log_entry in logs:

        time_str = log_entry.timestamp.strftime("%H:%M:%S")

        emoji = _get_log_emoji(log_entry.level)

        agent_name = log_entry.agent.replace(" AGENT", "")

        if log_entry.details:
            line = f"**{time_str}** {emoji} **{agent_name}**: {log_entry.action} - {log_entry.details}"
        else:
            line = (
                f"**{time_str}** {emoji} **{agent_name}**: {log_entry.action}"
            )

        log_lines.append(line)

    return "\n\n".join(log_lines)


def _get_log_emoji(level: LogLevel) -> str:
    """Get emoji for log level."""
    emoji_map = {
        LogLevel.INFO: "ℹ️",
        LogLevel.SUCCESS: "✅",
        LogLevel.WARNING: "⚠️",
        LogLevel.ERROR: "❌",
    }
    return emoji_map.get(level, "📝")
