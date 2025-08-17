import base64
from typing import Dict, List

import streamlit as st

from skillo.application.facades import ApplicationFacade


def extract_title_from_filename(filename: str) -> str:
    """Extract job title from filename by removing .pdf extension."""
    return filename.replace(".pdf", "").replace("-", " ").replace("_", " ")


def get_job_list_data(app_facade: ApplicationFacade) -> List[Dict[str, str]]:
    """Get job documents list with file paths and metadata."""
    try:
        documents = app_facade.documents.get_documents("job")
        return [
            {
                "document_id": doc.id,
                "filename": doc.metadata.get("filename", "Unknown"),
                "name": doc.metadata.get("name", "Unknown"),
                "job_title": doc.metadata.get("job_title", "Not specified"),
                "company": doc.metadata.get("contact", "Not specified"),
                "location": doc.metadata.get("location", "Not specified"),
                "required_skills": doc.metadata.get("skills", ""),
            }
            for doc in documents
        ]
    except Exception as e:
        st.error(f"Error getting job list data: {str(e)}")
        return []


def display_pdf_preview(pdf_bytes: bytes) -> None:
    """Display PDF preview from raw bytes."""
    try:
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")


def render(app_facade: ApplicationFacade) -> None:
    """Render the job listings page."""
    st.title("💼 Job List")
    st.markdown("Browse available job postings in the system")

    try:
        job_info_list = get_job_list_data(app_facade)

        if not job_info_list:
            st.warning("No job documents found in database")
            st.info("Go to 'Upload Documents' page to add job postings.")
            return

        st.success(f"Found {len(job_info_list)} job postings")

        st.subheader("Job List")

        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
        with col1:
            st.markdown("**Job Title**")
        with col2:
            st.markdown("**Company**")
        with col3:
            st.markdown("**Required Skills**")
        with col4:
            st.markdown("**Location**")
        with col5:
            st.markdown("**Preview**")

        for i, job_info in enumerate(job_info_list):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

            with col1:
                job_title = (
                    job_info["job_title"]
                    if job_info["job_title"] != "Not specified"
                    else extract_title_from_filename(job_info["filename"])
                )
                st.text(job_title)

            with col2:
                st.text(job_info["company"])

            with col3:
                st.text(job_info["required_skills"])

            with col4:
                st.text(job_info["location"])

            with col5:
                if st.button("👁️ Preview", key=f"job_preview_{i}"):
                    st.session_state.selected_job_info = job_info

        if (
            "selected_job_info" in st.session_state
            and st.session_state.selected_job_info
        ):
            st.markdown("---")
            selected_info = st.session_state.selected_job_info
            display_title = (
                selected_info["job_title"]
                if selected_info["job_title"] != "Not specified"
                else extract_title_from_filename(selected_info["filename"])
            )

            st.subheader(f"Preview: {display_title}")

            pdf_bytes = app_facade.documents.get_document_content(
                selected_info["filename"], "job"
            )
            if pdf_bytes:
                display_pdf_preview(pdf_bytes)
            else:
                st.error(
                    f"Cannot load PDF content for {selected_info['filename']}"
                )

    except Exception as e:
        st.error(f"Error loading job documents: {str(e)}")
