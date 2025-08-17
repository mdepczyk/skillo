import os

import streamlit as st

from skillo.application.facades import ApplicationFacade
from skillo.ui.views import (
    cv_list_page,
    job_list_page,
    management_page,
    match_page,
    stats_page,
    upload_page,
)


def run_ui(app_facade: ApplicationFacade) -> None:
    """Run Streamlit UI."""
    st.set_page_config(
        page_title="Skillo", layout="wide", initial_sidebar_state="expanded"
    )

    render_header()
    render_navigation(app_facade)


def render_header() -> None:
    """Render header and logo."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "assets", "logo.png")
    st.image(logo_path, width=300)
    st.markdown(
        "AI-powered CV and job posting matching using multi-agent analysis"
    )


def render_navigation(app_facade: ApplicationFacade) -> None:
    """Render navigation."""
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        [
            "Upload Documents",
            "CV List",
            "Job List",
            "Match Analysis",
            "Document Management",
            "Database Stats",
        ],
    )

    if page == "Upload Documents":
        upload_page.render(app_facade)
    elif page == "Match Analysis":
        match_page.render(app_facade)
    elif page == "Document Management":
        management_page.render(app_facade)
    elif page == "Database Stats":
        stats_page.render(app_facade)
    elif page == "CV List":
        cv_list_page.render(app_facade)
    elif page == "Job List":
        job_list_page.render(app_facade)
