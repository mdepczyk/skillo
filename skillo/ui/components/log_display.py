from typing import List

import streamlit as st

from skillo.application.dto import LogEntryDto, LogLevelDto
from skillo.application.facade import ApplicationFacade


def display_logs_section(
    app_facade: ApplicationFacade,
    title: str = "🔍 Logs",
    show_clear: bool = True,
) -> None:
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
            app_facade.clear_logs()
            st.rerun()

    logs = app_facade.get_logs()
    _render_logs(logs, app_facade)


def _render_logs(
    logs: List[LogEntryDto], app_facade: ApplicationFacade
) -> None:
    """Render log entries in Streamlit."""
    if not logs:
        st.info("No logs available.")
        return

    log_text = _format_logs_as_markdown(logs)

    with st.expander(f"Recent Logs ({len(logs)} total)", expanded=True):
        st.markdown(log_text)


def _format_logs_as_markdown(logs: List[LogEntryDto]) -> str:
    """Format log entries as markdown text."""
    log_lines = []

    for log_entry in logs:
        emoji = _get_log_emoji(log_entry.level)
        agent_name = log_entry.agent.replace(" AGENT", "")

        if log_entry.details:
            line = f"**{log_entry.timestamp}** {emoji} **{agent_name}**: {log_entry.action} - {log_entry.details}"
        else:
            line = f"**{log_entry.timestamp}** {emoji} **{agent_name}**: {log_entry.action}"

        log_lines.append(line)

    return "\n\n".join(log_lines)


def _get_log_emoji(level: str) -> str:
    """Get emoji for log level."""
    emoji_map = {
        LogLevelDto.INFO: "ℹ️",
        LogLevelDto.SUCCESS: "✅",
        LogLevelDto.WARNING: "⚠️",
        LogLevelDto.ERROR: "❌",
    }
    return emoji_map.get(level, "📝")
