from typing import Any, List

import streamlit as st

from skillo.application.facades import ApplicationFacade
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
    files: List[Any], file_type: str, app_facade: ApplicationFacade
) -> None:
    """Process and upload files in parallel with real-time progress."""
    if not files:
        st.warning("No files selected.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    def progress_update(completed: int, total: int) -> None:
        """Real-time progress callback for parallel processing."""
        progress = completed / total
        progress_bar.progress(progress)
        status_text.text(f"Processing {completed}/{total} files...")

    try:
        batch_result = (
            app_facade.documents.process_uploaded_documents_parallel(
                files, file_type, progress_update
            )
        )

        for result in batch_result.results:
            if result["success"]:
                st.success(f"✅ Successfully processed: {result['filename']}")
            else:
                st.error(
                    f"❌ Failed to process: {result['filename']} - {result['error']}"
                )

        progress_bar.progress(1.0)
        status_text.text("Processing complete!")

        if batch_result.successful_uploads > 0:
            st.success(
                f"✅ {batch_result.successful_uploads} files processed successfully"
            )
        if batch_result.failed_uploads > 0:
            st.error(
                f"❌ {batch_result.failed_uploads} files failed to process"
            )

        st.info(
            f"Upload Summary: {batch_result.successful_uploads} successful, {batch_result.failed_uploads} failed"
        )

    except Exception as e:
        st.error(f"❌ Parallel processing failed: {str(e)}")
        progress_bar.progress(1.0)
        status_text.text("Processing failed!")

    display_logs_section(app_facade, "🔍 Logs")
