import streamlit as st

from skillo.application.dto import ConfigDto, StatisticsDto
from skillo.application.facades import ApplicationFacade


def render(app_facade: ApplicationFacade) -> None:
    """Render database statistics page."""
    st.header("📊 Database Statistics")

    try:
        stats = app_facade.documents.get_statistics()
        config_values = app_facade.config.get_config_values()
        _render_document_counts(stats)
        _render_document_distribution(stats)
        _render_database_health(stats, config_values)
        _render_configuration_info(config_values)

    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")


def _render_document_counts(stats: StatisticsDto) -> None:
    """Render document counts."""
    try:
        total_docs = stats.total_documents
        cv_count = stats.cv_count
        job_count = stats.job_count

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Documents", total_docs)
        with col2:
            st.metric("CVs", cv_count)
        with col3:
            st.metric("Job Postings", job_count)

    except Exception as e:
        st.error(f"Error getting document counts: {str(e)}")


def _render_document_distribution(stats: StatisticsDto) -> None:
    """Render document type distribution chart."""
    try:
        cv_count = stats.cv_count
        job_count = stats.job_count
        total_docs = stats.total_documents

        if total_docs > 0:
            st.subheader("Document Distribution")

            chart_data = {
                "CVs": cv_count,
                "Job Postings": job_count,
            }

            st.bar_chart(chart_data)

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


def _render_database_health(
    stats: StatisticsDto, config_values: ConfigDto
) -> None:
    """Render database health information."""
    st.subheader("Database Health")

    try:
        total_docs = stats.total_documents

        if total_docs > 0:
            st.success("✅ Database is operational")

            st.info(f"📁 Vector store path: {config_values.chroma_db_path}")

            st.info(f"🗂️ Collection name: {config_values.collection_name}")

            try:
                cv_count = stats.cv_count
                job_count = stats.job_count
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


def _render_configuration_info(config_values: ConfigDto) -> None:
    """Render current configuration information."""
    st.subheader("Configuration")

    try:
        with st.expander("View Current Configuration"):

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Model Configuration**")
                st.text(f"Embedding Model: {config_values.embedding_model}")

                st.markdown("**Matching Configuration**")
                st.text(f"Min Match Score: {config_values.min_match_score}")
                st.text(
                    f"Top Candidates: {config_values.top_candidates_count}"
                )

            with col2:
                st.markdown("**Agent Weights**")
                weights = config_values.agent_weights
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
