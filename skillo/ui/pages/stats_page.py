"""Database Statistics page for Skillo."""

import pandas as pd
import streamlit as st

from skillo.config import Config
from skillo.core import VectorStore


def render(vector_store: VectorStore):
    """Render the database statistics page."""
    st.header("📊 Database Statistics")

    try:
        _render_document_counts(vector_store)
        _render_document_distribution(vector_store)
        _render_database_health(vector_store)
        _render_configuration_info()

    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")


def _render_document_counts(vector_store: VectorStore):
    """Render document count metrics."""
    try:

        total_docs = vector_store.get_document_count()
        cv_count = vector_store.get_document_count("cv")
        job_count = vector_store.get_document_count("job")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Documents", total_docs)
        with col2:
            st.metric("CVs", cv_count)
        with col3:
            st.metric("Job Postings", job_count)

    except Exception as e:
        st.error(f"Error getting document counts: {str(e)}")


def _render_document_distribution(vector_store: VectorStore):
    """Render document type distribution chart."""
    try:
        cv_count = vector_store.get_document_count("cv")
        job_count = vector_store.get_document_count("job")
        total_docs = cv_count + job_count

        if total_docs > 0:
            st.subheader("Document Distribution")

            chart_data = pd.DataFrame(
                {
                    "Document Type": ["CVs", "Job Postings"],
                    "Count": [cv_count, job_count],
                    "Percentage": [
                        (cv_count / total_docs) * 100,
                        (job_count / total_docs) * 100,
                    ],
                }
            )

            st.bar_chart(chart_data.set_index("Document Type")["Count"])

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "CV Percentage", f"{(cv_count / total_docs) * 100:.1f}%"
                )
            with col2:
                st.metric(
                    "Job Percentage", f"{(job_count / total_docs) * 100:.1f}%"
                )

    except Exception as e:
        st.error(f"Error creating distribution chart: {str(e)}")


def _render_database_health(vector_store: VectorStore):
    """Render database health information."""
    st.subheader("Database Health")

    try:
        total_docs = vector_store.get_document_count()

        if total_docs > 0:
            st.success("✅ Database is operational")

            config = Config()
            st.info(f"📁 Vector store path: {config.CHROMA_DB_PATH}")

            st.info(f"🗂️ Collection name: {config.COLLECTION_NAME}")

            if hasattr(vector_store, "collection") and vector_store.collection:
                try:

                    cv_count = vector_store.get_document_count("cv")
                    job_count = vector_store.get_document_count("job")
                    if cv_count + job_count > 0:

                        estimated_docs = cv_count + job_count
                        estimated_storage = estimated_docs * 5

                        if estimated_storage > 1024:
                            st.info(
                                f"💾 Estimated storage: {estimated_storage/1024:.1f} MB"
                            )
                        else:
                            st.info(
                                f"💾 Estimated storage: {estimated_storage:.1f} KB"
                            )

                except Exception:
                    pass

        else:
            st.warning("⚠️ No documents in database")
            st.info("Upload some documents to get started!")

    except Exception as e:
        st.error(f"Error checking database health: {str(e)}")


def _render_configuration_info():
    """Render current configuration information."""
    st.subheader("Configuration")

    try:
        config = Config()

        with st.expander("View Current Configuration"):

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Model Configuration**")
                st.text(f"Embedding Model: {config.EMBEDDING_MODEL}")

                st.markdown("**Matching Configuration**")
                st.text(f"Min Match Score: {config.MIN_MATCH_SCORE}")
                st.text(f"Top Candidates: {config.TOP_CANDIDATES_COUNT}")

            with col2:
                st.markdown("**Agent Weights**")
                weights = config.AGENT_WEIGHTS
                for agent, weight in weights.items():
                    st.text(f"{agent.title()}: {weight:.2f}")

                total_weight = sum(weights.values())
                if abs(total_weight - 1.0) < 0.01:
                    st.success(f"✅ Weights sum: {total_weight:.3f}")
                else:
                    st.warning(
                        f"⚠️ Weights sum: {total_weight:.3f} (should be 1.0)"
                    )

    except Exception as e:
        st.error(f"Error displaying configuration: {str(e)}")


def _render_performance_metrics():
    """Render performance metrics if available."""
