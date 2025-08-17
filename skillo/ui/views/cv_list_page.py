import base64
from typing import Dict, List

import streamlit as st

from skillo.application.facades import ApplicationFacade


def extract_name_from_filename(filename: str) -> str:
    """Extract name from filename by removing .pdf extension."""
    return filename.replace(".pdf", "").replace("-", " ").replace("_", " ")


def get_cv_list_data(app_facade: ApplicationFacade) -> List[Dict[str, str]]:
    """Get CV documents list with file paths and metadata."""
    try:
        documents = app_facade.documents.get_documents("cv")
        return [
            {
                "document_id": doc.id,
                "filename": doc.metadata.get("filename", "Unknown"),
                "name": doc.metadata.get("name", "Unknown"),
                "contact": doc.metadata.get("contact", "Not specified"),
                "location": doc.metadata.get("location", "Not specified"),
                "skills": doc.metadata.get("skills", ""),
                "profile": doc.metadata.get("job_title", "Unknown"),
            }
            for doc in documents
        ]
    except Exception as e:
        st.error(f"Error getting CV list data: {str(e)}")
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
    """Render the CV list page."""
    st.title("📄 CV List")
    st.markdown("Browse available CVs in the system")

    try:
        cv_info_list = get_cv_list_data(app_facade)

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
            display_name = (
                selected_info["name"]
                if selected_info["name"] != "Unknown"
                else extract_name_from_filename(selected_info["filename"])
            )

            st.subheader(f"Preview: {display_name}")

            pdf_bytes = app_facade.documents.get_document_content(
                selected_info["filename"], "cv"
            )
            if pdf_bytes:
                display_pdf_preview(pdf_bytes)
            else:
                st.error(
                    f"Cannot load PDF content for {selected_info['filename']}"
                )

    except Exception as e:
        st.error(f"Error loading CV documents: {str(e)}")
