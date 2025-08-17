from typing import List

import streamlit as st

from skillo.application.facade import ApplicationFacade
from skillo.ui.components.log_display import display_logs_section


def render(app_facade: ApplicationFacade) -> None:
    """Render upload documents page."""
    st.header("📄 Upload Documents")

    col1, col2 = st.columns(2)

    with col1:
        _render_cv_upload_section(app_facade)

    with col2:
        _render_job_upload_section(app_facade)


def _render_cv_upload_section(app_facade: ApplicationFacade) -> None:
    """Render CV upload section."""
    st.subheader("Upload CVs")
    cv_files = st.file_uploader(
        "Choose CV PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="cv_uploader",
    )

    if cv_files:
        if st.button("Process CV Files", key="process_cvs"):
            _process_files(cv_files, "cv", app_facade)


def _render_job_upload_section(app_facade: ApplicationFacade) -> None:
    """Render job upload section."""
    st.subheader("Upload Job Postings")
    job_files = st.file_uploader(
        "Choose Job PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="job_uploader",
    )

    if job_files:
        if st.button("Process Job Files", key="process_jobs"):
            _process_files(job_files, "job", app_facade)


def _process_files(
    files: List, file_type: str, app_facade: ApplicationFacade
) -> None:
    """Process uploaded files."""
    if not files:
        st.warning("No files selected.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    successful_uploads = 0
    failed_uploads = 0

    for i, file in enumerate(files):
        status_text.text(f"Processing {file.name}...")

        try:
            document_dto = app_facade.process_document(file, file_type)

            if document_dto:
                if app_facade.upload_document_dto(document_dto):
                    successful_uploads += 1
                    st.success(f"✅ Successfully processed: {file.name}")
                else:
                    failed_uploads += 1
                    st.error(f"❌ Failed to add to database: {file.name}")
            else:
                failed_uploads += 1
                st.error(f"❌ Failed to process: {file.name}")

        except Exception as e:
            failed_uploads += 1
            st.error(f"❌ Error processing {file.name}: {str(e)}")

        progress_bar.progress((i + 1) / len(files))

    status_text.text("Processing complete!")

    if successful_uploads > 0:
        st.success(f"✅ {successful_uploads} files processed successfully")
    if failed_uploads > 0:
        st.error(f"❌ {failed_uploads} files failed to process")

    st.info(
        f"Upload Summary: {successful_uploads} successful, {failed_uploads} failed"
    )

    display_logs_section(app_facade, "🔍 Logs")
