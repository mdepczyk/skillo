"""Match Analysis page for Skillo."""

import streamlit as st

from skillo.core import JobMatcher, VectorStore
from skillo.ui.components.matching import MatchResultsDisplay
from skillo.ui.components.log_display import display_logs_section


def render(matcher: JobMatcher, vector_store: VectorStore):
    """Render the match analysis page."""
    st.header("🔍 Match Analysis")

    analysis_type = st.radio(
        "Choose analysis type:",
        ["Find jobs for a CV", "Find candidates for a job"],
    )

    if analysis_type == "Find jobs for a CV":
        _render_cv_to_jobs_analysis(matcher, vector_store)
    else:
        _render_job_to_cvs_analysis(matcher, vector_store)

    display_logs_section("🔍 Analysis Logs")


def _render_cv_to_jobs_analysis(
    matcher: JobMatcher, vector_store: VectorStore
):
    """Render CV to jobs analysis section."""
    st.subheader("Find Jobs for CV")

    cv_documents = vector_store.get_all_documents_for_matching(doc_type="cv")

    if not cv_documents:
        st.warning("No CVs found in database. Please upload some CVs first.")
        return

    cv_options = {}
    for doc in cv_documents:
        structured_data = doc.get("structured_data", {})
        name = structured_data.get("name", "Unknown")
        profile = structured_data.get("profile", "Unknown")
        display_name = f"{name} - {profile}"
        cv_options[display_name] = doc

    selected_cv_name = st.selectbox("Select a CV:", list(cv_options.keys()))

    if selected_cv_name and st.button("Find Matching Jobs"):
        selected_cv = cv_options[selected_cv_name]

        progress_container = st.empty()

        with st.spinner("Analyzing matches..."):
            try:

                progress_container.info("🚀 Starting CV to jobs analysis...")
                matches = matcher.match_cv_to_all_jobs(selected_cv)

                progress_container.empty()

                if matches:
                    st.success(f"Found {len(matches)} job matches")
                    MatchResultsDisplay.display_job_matches(matches)
                else:
                    st.warning("No matching jobs found.")

            except Exception as e:
                progress_container.empty()
                st.error(f"Error during matching: {str(e)}")


def _render_job_to_cvs_analysis(
    matcher: JobMatcher, vector_store: VectorStore
):
    """Render job to CVs analysis section."""
    st.subheader("Find Candidates for Job")

    job_documents = vector_store.get_all_documents_for_matching(doc_type="job")

    if not job_documents:
        st.warning(
            "No job postings found in database. Please upload some job postings first."
        )
        return

    job_options = {}
    for doc in job_documents:
        structured_data = doc.get("structured_data", {})
        company = structured_data.get("company", "Unknown Company")
        job_title = structured_data.get("job_title", "Unknown Position")
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
                matches = matcher.match_job_to_all_cvs(selected_job)

                progress_container.empty()

                if matches:
                    st.success(f"Found {len(matches)} candidate matches")
                    MatchResultsDisplay.display_candidate_matches(matches)
                else:
                    st.warning("No matching candidates found.")

            except Exception as e:
                progress_container.empty()
                st.error(f"Error during matching: {str(e)}")
