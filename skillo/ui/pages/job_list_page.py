"""Job listings page with PDF preview functionality."""

import base64
import os
from typing import Any, Dict, List

import streamlit as st

from skillo.core import VectorStore


def extract_title_from_filename(filename: str) -> str:
    """Extract job title from filename by removing .pdf extension."""
    return filename.replace(".pdf", "").replace("-", " ").replace("_", " ")


def get_job_info(vector_store: VectorStore) -> List[Dict[str, Any]]:
    """Get job documents with parsed information."""
    try:

        job_documents = vector_store.get_all_documents_for_matching("job")

        job_info = []
        for document in job_documents:
            structured_data = document.get("structured_data", {})

            job_title = "Not specified"
            company = "Not specified"
            location = "Not specified"
            required_skills = "Not specified"

            sections = structured_data.get("sections", {})

            job_title_section = sections.get("job_title", "")
            if job_title_section:
                lines = job_title_section.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        job_title = line
                        break

            company_section = sections.get("company", "")
            if company_section:
                lines = company_section.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        company = line
                        break

            location_section = sections.get("location", "")
            if location_section and "Not specified" not in location_section:
                lines = location_section.split("\n")
                for line in lines:
                    line = line.strip()
                    if (
                        line
                        and not line.startswith("#")
                        and not line.startswith("-")
                    ):
                        location = line
                        break

            skills_section = sections.get("required_skills", "")
            if skills_section:
                skill_list = []
                lines = skills_section.split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("-"):
                        skill = line.replace("-", "").strip()
                        skill_list.append(skill)
                        if len(skill_list) >= 3:
                            break
                if skill_list:
                    required_skills = ", ".join(skill_list)

            job_info.append(
                {
                    "document_id": document["id"],
                    "filename": document["metadata"]["filename"],
                    "file_path": document["metadata"]["file_path"],
                    "job_title": job_title,
                    "company": company,
                    "location": location,
                    "required_skills": required_skills,
                }
            )

        return job_info

    except Exception as e:
        st.error(f"Error getting job info: {str(e)}")
        return []


def display_pdf_preview(file_path: str):
    """Display PDF preview using base64 encoding."""
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")

        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")


def render(vector_store: VectorStore):
    """Render the job listings page."""
    st.title("💼 Job List")
    st.markdown("Browse available job postings in the system")

    try:

        job_info_list = get_job_info(vector_store)

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
            filename = selected_info["filename"]
            file_path = selected_info["file_path"]
            display_title = (
                selected_info["job_title"]
                if selected_info["job_title"] != "Not specified"
                else extract_title_from_filename(filename)
            )

            st.subheader(f"Preview: {display_title}")

            if os.path.exists(file_path):
                display_pdf_preview(file_path)
            else:
                st.error(f"File {file_path} does not exist")

    except Exception as e:
        st.error(f"Error loading job documents: {str(e)}")
