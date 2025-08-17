import streamlit as st

from skillo.application.facades import ApplicationFacade
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

    stats = app_facade.documents.get_statistics()
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

        progress_bar = st.progress(0)
        status_text = st.empty()

        def progress_update(completed: int, total: int) -> None:
            """Real-time progress callback for CV matching."""
            progress = completed / total
            progress_bar.progress(progress)
            status_text.text(f"Analyzing {completed}/{total} jobs...")

        try:
            status_text.text("🚀 Starting CV to jobs analysis...")
            matches = app_facade.matching.match_cv_to_jobs_with_progress(
                selected_cv, progress_update
            )

            progress_bar.progress(1.0)
            status_text.text("Analysis complete!")

            if matches:
                MatchResultsDisplay.display_job_matches(matches)

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"CV matching error: {str(e)}")


def _render_job_to_cvs_analysis(app_facade: ApplicationFacade) -> None:
    """Render job to CVs analysis section."""
    st.subheader("Find Candidates for Job")

    stats = app_facade.documents.get_statistics()
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

        progress_bar = st.progress(0)
        status_text = st.empty()

        def progress_update(completed: int, total: int) -> None:
            """Real-time progress callback for job matching."""
            progress = completed / total
            progress_bar.progress(progress)
            status_text.text(f"Analyzing {completed}/{total} candidates...")

        try:
            status_text.text("🚀 Starting job to candidates analysis...")
            matches = app_facade.matching.match_job_to_cvs_with_progress(
                selected_job, progress_update
            )

            progress_bar.progress(1.0)
            status_text.text("Analysis complete!")

            if matches:
                MatchResultsDisplay.display_candidate_matches(matches)

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Job matching error: {str(e)}")
