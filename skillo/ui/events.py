from typing import Dict, Any
import streamlit as st


class StreamlitMatchingEvents:
    """Streamlit implementation of matching events using st.info, st.warning, etc."""
    
    def on_no_documents_found(self, doc_type: str) -> None:
        """Show warning when no documents found."""
        if doc_type == "job":
            st.warning("No job postings found in database")
        elif doc_type == "cv":
            st.warning("No CVs found in database")
    
    def on_prefiltering_started(self, count: int, doc_type: str) -> None:
        """Show info about prefiltering process."""
        if doc_type == "job":
            st.info(f"🔍 Pre-filtering {count} job postings by semantic similarity...")
        elif doc_type == "cv":
            st.info(f"🔍 Pre-filtering {count} candidate profiles by semantic similarity...")
    
    def on_documents_found(self, count: int, doc_type: str) -> None:
        """Show success when documents retrieved."""
        if doc_type == "job":
            st.success(f"✅ Found {count} job postings, analyzing matches...")
        elif doc_type == "cv":
            st.success(f"✅ Found {count} candidate profiles, analyzing matches...")
    
    def on_no_matches_after_prefiltering(self, doc_type: str) -> None:
        """Show warning when no matches after prefiltering."""
        if doc_type == "job":
            st.warning("No jobs passed similarity pre-filtering")
        elif doc_type == "cv":
            st.warning("No CVs passed similarity pre-filtering")
    
    def on_matching_started(self, cv_name: str, job_info: str) -> None:
        """Show info about specific matching process."""
        if cv_name and job_info:
            st.info(f"🎯 Analyzing match: {cv_name} ↔ {job_info}")
    
    def on_matching_error(self, error_msg: str, context: str) -> None:
        """Show error during matching process."""
        st.error(f"❌ {context}: {error_msg}")
    
    def on_match_completed(self, result: Dict[str, Any]) -> None:
        """Show completion of matching process."""
        st.success(f"✅ Match completed with score: {result.get('weighted_final_score', 0):.2f}")
    
    def on_max_candidates_reached(self, max_count: int) -> None:
        """Show info when maximum candidates limit reached."""
        st.info(f"🛑 Reached max candidates ({max_count}), stopping analysis")
    
    def on_document_not_processed(self, filename: str, doc_type: str) -> None:
        """Show error when document is not processed."""
        doc_name = "CV" if doc_type == "cv" else "Job" 
        st.error(
            f"{doc_name} {filename} is not processed. Please process with Document Processing Agent first!"
        )