import streamlit as st

from skillo.application.facade import ApplicationFacade
from skillo.ui.components.log_display import display_logs_section
from skillo.ui.components.matching import MatchResultsDisplay


def render(app_facade: ApplicationFacade) -> None:
    """Render match analysis page."""
    st.header("🔍 Match Analysis")

    analysis_type = st.radio(
        "Choose analysis type:",
        ["Find jobs for a CV", "Find candidates for a job"],
    )

    if analysis_type == "Find jobs for a CV":
        _render_cv_to_jobs_analysis(app_facade)
    else:
        _render_job_to_cvs_analysis(app_facade)

    display_logs_section(app_facade, "🔍 Logs")


def _render_cv_to_jobs_analysis(app_facade: ApplicationFacade) -> None:
    """Render CV to jobs analysis."""
    st.subheader("Find Jobs for CV")

    stats = app_facade.get_statistics()
    cv_documents = stats.cv_documents

    if not cv_documents:
        st.warning("No CVs found in database. Please upload some CVs first.")
        return

    cv_options = {}
    for doc in cv_documents:
        name = doc.metadata.get("name", "Unknown")
        profile = doc.metadata.get("job_title", "Unknown Position")
        display_name = f"{name} - {profile}"
        cv_options[display_name] = doc

    selected_cv_name = st.selectbox("Select a CV:", list(cv_options.keys()))

    if selected_cv_name and st.button("Find Matching Jobs"):
        selected_cv = cv_options[selected_cv_name]

        progress_container = st.empty()

        with st.spinner("Analyzing matches..."):
            try:

                progress_container.info("🚀 Starting CV to jobs analysis...")
                matches = app_facade.match_cv_to_jobs_dto(selected_cv)

                progress_container.empty()

                if matches:
                    st.success(f"Found {len(matches)} job matches")
                    MatchResultsDisplay.display_job_matches(matches)
                else:
                    st.warning("No matching jobs found.")

            except Exception as e:
                progress_container.empty()
                st.error(f"Error during matching: {str(e)}")


def _render_job_to_cvs_analysis(app_facade: ApplicationFacade) -> None:
    """Render job to CVs analysis section."""
    st.subheader("Find Candidates for Job")

    stats = app_facade.get_statistics()
    job_documents = stats.job_documents

    if not job_documents:
        st.warning(
            "No job postings found in database. Please upload some job postings first."
        )
        return

    job_options = {}
    for doc in job_documents:
        company = doc.metadata.get("contact", "Unknown Company")
        job_title = doc.metadata.get("job_title", "Unknown Position")
        display_name = f"{company} - {job_title}"
        job_options[display_name] = doc

    selected_job_name = st.selectbox(
        "Select a job posting:", list(job_options.keys())
    )

    if selected_job_name and st.button("Find Matching Candidates"):
        selected_job = job_options[selected_job_name]

        progress_container = st.empty()

        with st.spinner("Analyzing matches..."):
            try:

                progress_container.info(
                    "🚀 Starting job to candidates analysis..."
                )
                matches = app_facade.match_job_to_cvs_dto(selected_job)

                progress_container.empty()

                if matches:
                    st.success(f"Found {len(matches)} candidate matches")
                    MatchResultsDisplay.display_candidate_matches(matches)
                else:
                    st.warning("No matching candidates found.")

            except Exception as e:
                progress_container.empty()
                st.error(f"Error during matching: {str(e)}")
