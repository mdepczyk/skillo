import pandas as pd
import streamlit as st

from skillo.application.facade import ApplicationFacade


def render(app_facade: ApplicationFacade) -> None:
    """Render the document management page."""
    st.header("📚 Document Management")

    tab1, tab2 = st.tabs(["View Documents", "Database Actions"])

    with tab1:
        _render_documents_view(app_facade)

    with tab2:
        _render_database_actions(app_facade)


def _render_documents_view(app_facade: ApplicationFacade) -> None:
    """Render the documents view tab."""
    st.subheader("Current Documents")

    doc_type = st.selectbox("Filter by type:", ["All", "CV", "Job"])

    try:
        stats = app_facade.get_statistics()

        if doc_type == "All":
            documents = stats.cv_documents + stats.job_documents
        elif doc_type == "CV":
            documents = stats.cv_documents
        else:
            documents = stats.job_documents

        if documents:

            doc_data = []
            for doc in documents:
                doc_id = doc.id
                filename = doc.metadata.get("filename", "Unknown")
                doc_type = doc.document_type

                doc_data.append(
                    {
                        "ID": doc_id,
                        "Filename": filename,
                        "Type": doc_type.upper(),
                        "Content": doc.content,
                        "Metadata": str(doc.metadata),
                    }
                )

            df = pd.DataFrame(doc_data)
            st.dataframe(df, use_container_width=True)

            total_docs = len(documents)
            cv_count = sum(1 for doc in documents if doc.document_type == "cv")
            job_count = sum(
                1 for doc in documents if doc.document_type == "job"
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Documents", total_docs)
            with col2:
                st.metric("CVs", cv_count)
            with col3:
                st.metric("Jobs", job_count)

        else:
            st.info("No documents found in database.")

    except Exception as e:
        st.error(f"Error retrieving documents: {str(e)}")


def _render_database_actions(app_facade: ApplicationFacade) -> None:
    """Render the database actions tab."""
    st.subheader("Database Actions")

    col1, col2 = st.columns(2)

    with col1:
        _render_reset_section(app_facade)

    with col2:
        _render_export_section(app_facade)


def _render_reset_section(app_facade: ApplicationFacade) -> None:
    """Render the database reset section."""
    st.markdown("**Reset Database**")
    st.warning("This will delete all documents and embeddings!")

    if "show_reset_confirmation" not in st.session_state:
        st.session_state.show_reset_confirmation = False

    if st.button("🗑️ Reset Database", type="secondary"):
        st.session_state.show_reset_confirmation = True

    if st.session_state.show_reset_confirmation:
        st.markdown("---")
        confirm_reset = st.checkbox(
            "✅ I confirm I want to reset the database"
        )

        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button(
                "🔥 Confirm Reset", type="primary", disabled=not confirm_reset
            ):
                try:
                    if app_facade.reset_database():

                        st.session_state.database_reset = True
                        st.session_state.show_reset_confirmation = False
                        st.success("Database reset successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to reset database.")
                except Exception as e:
                    st.error(f"Error resetting database: {str(e)}")

        with col_cancel:
            if st.button("❌ Cancel"):
                st.session_state.show_reset_confirmation = False
                st.rerun()


def _render_export_section(app_facade: ApplicationFacade) -> None:
    """Render the data export section."""
    st.markdown("**Export Data**")

    try:
        stats = app_facade.get_statistics()
        total_documents = stats.total_documents

        if total_documents > 0:
            try:
                csv_content = app_facade.export_to_csv()

                st.download_button(
                    label="📥 Export to CSV",
                    data=csv_content,
                    file_name=f"skillo_documents_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )

            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
        else:
            st.warning("No documents to export.")

    except Exception as e:
        st.error(f"Error preparing export: {str(e)}")
