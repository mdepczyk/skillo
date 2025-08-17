"""CV list page with PDF preview functionality."""

import base64
import os
from typing import Any, Dict, List

import streamlit as st

from skillo.core import VectorStore


def extract_name_from_filename(filename: str) -> str:
    """Extract name from filename by removing .pdf extension."""
    return filename.replace(".pdf", "").replace("-", " ").replace("_", " ")


def get_cv_personal_info(vector_store: VectorStore) -> List[Dict[str, Any]]:
    """Get CV documents with structured data."""
    try:

        cv_documents = vector_store.get_all_documents_for_matching("cv")

        cv_info = []
        for document in cv_documents:
            structured_data = document.get("structured_data", {})

            name = structured_data.get("name", "Not specified")
            contact = "Not specified"
            location = "Not specified"
            skills = "Not specified"
            profile = "Unknown"

            sections = structured_data.get("sections", {})

            personal_info_section = sections.get("personal_information", "")
            if personal_info_section:
                lines = personal_info_section.split("\n")
                for line in lines:
                    line = line.strip()
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if key == "contact":
                            contact = value

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

            skills_section = sections.get("skills", "")
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
                    skills = ", ".join(skill_list)

            profile = structured_data.get("profile", "Unknown")

            cv_info.append(
                {
                    "document_id": document["id"],
                    "filename": document["metadata"]["filename"],
                    "file_path": document["metadata"]["file_path"],
                    "name": name,
                    "contact": contact,
                    "location": location,
                    "skills": skills,
                    "profile": profile,
                }
            )

        return cv_info

    except Exception as e:
        st.error(f"Error getting CV personal info: {str(e)}")
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
    """Render the CV list page."""
    st.title("📄 CV List")
    st.markdown("Browse available CVs in the system")

    try:

        cv_info_list = get_cv_personal_info(vector_store)

        if not cv_info_list:
            st.warning("No CV documents found in database")
            st.info("Go to 'Upload Documents' page to add CVs.")
            return

        st.success(f"Found {len(cv_info_list)} CV documents")

        st.subheader("CV List")

        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
        with col1:
            st.markdown("**Name**")
        with col2:
            st.markdown("**Contact**")
        with col3:
            st.markdown("**Skills**")
        with col4:
            st.markdown("**Location**")
        with col5:
            st.markdown("**Profile**")
        with col6:
            st.markdown("**Preview**")

        for i, cv_info in enumerate(cv_info_list):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])

            with col1:
                name = (
                    cv_info["name"]
                    if cv_info["name"]
                    else extract_name_from_filename(cv_info["filename"])
                )
                st.text(name)

            with col2:
                st.text(cv_info["contact"])

            with col3:
                st.text(cv_info["skills"])

            with col4:
                st.text(cv_info["location"])

            with col5:
                st.text(cv_info["profile"])

            with col6:
                if st.button("👁️ Preview", key=f"cv_preview_{i}"):
                    st.session_state.selected_cv_info = cv_info

        if (
            "selected_cv_info" in st.session_state
            and st.session_state.selected_cv_info
        ):
            st.markdown("---")
            selected_info = st.session_state.selected_cv_info
            filename = selected_info["filename"]
            file_path = selected_info["file_path"]
            display_name = (
                selected_info["name"]
                if selected_info["name"]
                else extract_name_from_filename(filename)
            )

            st.subheader(f"Preview: {display_name}")

            if os.path.exists(file_path):
                display_pdf_preview(file_path)
            else:
                st.error(f"File {file_path} does not exist")

    except Exception as e:
        st.error(f"Error loading CV documents: {str(e)}")
