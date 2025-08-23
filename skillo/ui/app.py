import os
import sys
import streamlit as st

from skillo.agents import LangChainCVProcessingAgent, LangChainJobProcessingAgent, LangChainNormalizationAgent
from skillo.tools.profile_classifier import ProfileClassifier
from skillo.config import validate_config, Config
from skillo.core import DocumentProcessor, JobMatcher, VectorStore
from skillo.ui.events import StreamlitMatchingEvents
from skillo.ui.pages import (
    cv_list_page,
    job_list_page,
    management_page,
    match_page,
    stats_page,
    upload_page,
)


project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


st.set_page_config(
    page_title="Skillo", layout="wide", initial_sidebar_state="expanded"
)


@st.cache_resource
def initialize_components():
    """Initialize and cache application components."""
    try:
        validate_config()
        config = Config()
        events = StreamlitMatchingEvents()
        
        profile_classifier = ProfileClassifier()
        cv_agent = LangChainCVProcessingAgent(profile_classifier)
        job_agent = LangChainJobProcessingAgent()
        normalizer = LangChainNormalizationAgent()
        
        processor = DocumentProcessor(config, cv_agent, job_agent, normalizer)
        vector_store = VectorStore()
        matcher = JobMatcher(config, events)
        return processor, vector_store, matcher
    except Exception as e:
        st.error(f"Error initializing components: {str(e)}")
        return None, None, None


def reinitialize_components_after_reset():
    """Reinitialize components after database reset."""
    try:
        initialize_components.clear()
        config = Config()
        events = StreamlitMatchingEvents()
        
        profile_classifier = ProfileClassifier()
        cv_agent = LangChainCVProcessingAgent(profile_classifier)
        job_agent = LangChainJobProcessingAgent()
        normalizer = LangChainNormalizationAgent()
        
        processor = DocumentProcessor(config, cv_agent, job_agent, normalizer)
        vector_store = VectorStore()
        matcher = JobMatcher(config, events)
        return processor, vector_store, matcher
    except Exception as e:
        st.error(f"Error reinitializing components: {str(e)}")
        return None, None, None


def main():
    logo_path = os.path.join(
        project_root, "skillo", "ui", "assets", "logo.png"
    )
    st.image(logo_path, width=300)
    st.markdown(
        "AI-powered CV and job posting matching using multi-agent analysis"
    )

    if (
        "database_reset" in st.session_state
        and st.session_state.database_reset
    ):
        processor, vector_store, matcher = (
            reinitialize_components_after_reset()
        )
        st.session_state.database_reset = False
    else:

        processor, vector_store, matcher = initialize_components()

    if not all([processor, vector_store, matcher]):
        st.error(
            "Failed to initialize application components. Please check your configuration."
        )
        st.info("Make sure to set your OPENAI_API_KEY environment variable.")
        return

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        [
            "Upload Documents",
            "CV List",
            "Job List",
            "Match Analysis",
            "Document Management",
            "Database Stats",
        ],
    )

    if page == "Upload Documents":
        upload_page.render(processor, vector_store)
    elif page == "Match Analysis":
        match_page.render(matcher, vector_store)
    elif page == "Document Management":
        management_page.render(vector_store)
    elif page == "Database Stats":
        stats_page.render(vector_store)
    elif page == "CV List":
        cv_list_page.render(vector_store)
    elif page == "Job List":
        job_list_page.render(vector_store)


if __name__ == "__main__":
    main()
