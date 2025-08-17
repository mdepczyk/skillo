"""Document Management page for Skillo."""

import pandas as pd
import streamlit as st

from skillo.core import VectorStore
from skillo.utils.helpers import truncate_text


def render(vector_store: VectorStore):
    """Render the document management page."""
    st.header("📚 Document Management")

    tab1, tab2 = st.tabs(["View Documents", "Database Actions"])

    with tab1:
        _render_documents_view(vector_store)

    with tab2:
        _render_database_actions(vector_store)


def _render_documents_view(vector_store: VectorStore):
    """Render the documents view tab."""
    st.subheader("Current Documents")

    doc_type = st.selectbox("Filter by type:", ["All", "CV", "Job"])

    try:
        if doc_type == "All":

            cv_documents = vector_store.get_all_documents("cv")
            job_documents = vector_store.get_all_documents("job")
            documents = cv_documents + job_documents
        else:
            documents = vector_store.get_all_documents(doc_type.lower())

        if documents:

            doc_data = []
            for doc in documents:
                doc_data.append(
                    {
                        "ID": truncate_text(doc["id"], 12),
                        "Filename": doc["metadata"]["filename"],
                        "Type": doc["document_type"].upper(),
                        "Path": doc["metadata"]["file_path"],
                    }
                )

            df = pd.DataFrame(doc_data)
            st.dataframe(df, use_container_width=True)

            total_docs = len(documents)
            cv_count = sum(
                1 for doc in documents if doc["document_type"] == "cv"
            )
            job_count = sum(
                1 for doc in documents if doc["document_type"] == "job"
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


def _render_database_actions(vector_store: VectorStore):
    """Render the database actions tab."""
    st.subheader("Database Actions")

    col1, col2 = st.columns(2)

    with col1:
        _render_reset_section(vector_store)

    with col2:
        _render_export_section(vector_store)


def _render_reset_section(vector_store: VectorStore):
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
                    if vector_store.reset_database():

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


def _render_export_section(vector_store: VectorStore):
    """Render the data export section."""
    st.markdown("**Export Data**")

    try:

        cv_documents = vector_store.get_all_documents("cv")
        job_documents = vector_store.get_all_documents("job")
        all_documents = cv_documents + job_documents

        if all_documents:
            if st.button("📥 Export Data"):
                chunks_data = _export_chunks_csv(vector_store)
                st.download_button(
                    label="Download Chunks CSV",
                    data=chunks_data,
                    file_name="skillo_chunks.csv",
                    mime="text/csv",
                )
        else:
            st.warning("No documents to export.")

    except Exception as e:
        st.error(f"Error preparing export: {str(e)}")


def _export_chunks_csv(vector_store) -> str:
    """Export all chunks from ChromaDB as CSV - shows chunked structure."""
    try:

        collection = vector_store.collection
        results = collection.get(include=["documents", "metadatas"])

        chunk_data = []
        if results["documents"]:
            for i in range(len(results["documents"])):
                chunk_metadata = results["metadatas"][i]
                chunk_content = results["documents"][i]

                chunk_data.append(
                    {
                        "Chunk_ID": results["ids"][i],
                        "Document_ID": chunk_metadata.get(
                            "document_id", "unknown"
                        ),
                        "Filename": chunk_metadata.get("filename", "unknown"),
                        "Document_Type": chunk_metadata.get(
                            "document_type", "unknown"
                        ),
                        "Section": chunk_metadata.get("section", "unknown"),
                        "Content_Length": len(chunk_content),
                        "Content_Preview": (
                            chunk_content[:200] + "..."
                            if len(chunk_content) > 200
                            else chunk_content
                        ),
                        "File_Path": chunk_metadata.get(
                            "file_path", "unknown"
                        ),
                    }
                )

        df = pd.DataFrame(chunk_data)
        return df.to_csv(index=False)

    except Exception as e:
        st.error(f"Error exporting chunks: {str(e)}")
        return "Error,Message\nExport Error,Failed to export chunks"
