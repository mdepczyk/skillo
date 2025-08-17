"""UI components for displaying matching results."""

from typing import Any, Dict, List

import streamlit as st

from skillo.utils.helpers import format_score


class MatchResultsDisplay:
    """Class for displaying match results in the UI."""

    @staticmethod
    def display_job_matches(matches: List[Dict[str, Any]]):
        """Display job match results."""
        for i, match in enumerate(matches, 1):
            job_info = match.get("job_info", {})
            company = job_info.get("company", "Unknown Company")
            job_title = job_info.get("job_title", "Unknown Position")
            job_display = f"{company} - {job_title}"

            with st.expander(
                f"#{i} {job_display} - Score: {format_score(match['weighted_final_score'])}"
            ):
                MatchResultsDisplay._render_match_details(match, f"job_{i}")

    @staticmethod
    def display_candidate_matches(matches: List[Dict[str, Any]]):
        """Display candidate match results."""
        for i, match in enumerate(matches, 1):
            cv_info = match.get("cv_info", {})
            name = cv_info.get("name", "Unknown")
            profile = cv_info.get("profile", "Unknown")
            candidate_display = f"{name} - {profile}"

            with st.expander(
                f"#{i} {candidate_display} - Score: {format_score(match['weighted_final_score'])}"
            ):
                MatchResultsDisplay._render_match_details(
                    match, f"candidate_{i}"
                )

    @staticmethod
    def _render_match_details(match: Dict[str, Any], unique_key: str):
        """Render detailed match information with improved layout."""

        col1, col2 = st.columns([1, 3])

        with col1:
            MatchResultsDisplay._render_scores_section(match)

        with col2:
            MatchResultsDisplay._render_summary_section(match, unique_key)

    @staticmethod
    def _render_scores_section(match: Dict[str, Any]):
        """Render final score and individual agent scores."""

        final_score = match["weighted_final_score"]
        match_category = match.get("recommendation", "Unknown")

        st.metric(
            "Final Score", format_score(final_score), delta=f"{match_category}"
        )

        st.markdown("**Agent Scores**")

        agent_scores = {
            "Skills": match.get("skills_score", 0.0),
            "Location": match.get("location_score", 0.0),
            "Experience": match.get("experience_score", 0.0),
            "Preferences": match.get("preferences_score", 0.0),
            "Semantic": match.get("semantic_score", 0.0),
        }

        for agent_name, score in agent_scores.items():
            st.metric(agent_name, format_score(score))

    @staticmethod
    def _render_summary_section(match: Dict[str, Any], unique_key: str):
        """Render detailed agent analysis directly."""
        st.markdown("**Detailed Agent Analysis**")

        MatchResultsDisplay._display_detailed_analysis(
            match.get("detailed_results", {}), unique_key
        )

    @staticmethod
    def _display_detailed_analysis(
        agent_results: Dict[str, Any], unique_key: str
    ):
        """Display detailed analysis from all agents."""

        for agent_name, result in agent_results.items():
            with st.expander(f"{agent_name.title()} Agent Analysis"):

                explanation = result.get(
                    "explanation", "No explanation available"
                )

                formatted_explanation = explanation.replace(
                    " | ", "\n\n• "
                ).replace("|", "\n\n• ")
                st.text_area(
                    "Analysis",
                    formatted_explanation,
                    height=180,
                    key=f"detail_explanation_{agent_name}_{unique_key}",
                )

                MatchResultsDisplay._render_agent_specific_details(
                    agent_name, result
                )

                st.markdown("---")

    @staticmethod
    def _render_agent_specific_details(
        agent_name: str, result: Dict[str, Any]
    ):
        """Render agent-specific detail information."""

        if agent_name == "location":
            if "candidate_location" in result:
                st.text(
                    f"📍 Candidate: {result.get('candidate_location', 'N/A')}"
                )
                st.text(f"📍 Job: {result.get('job_location', 'N/A')}")
                st.text(f"🏠 Remote: {result.get('remote_work', 'N/A')}")

        elif agent_name == "skills":
            matched_skills = result.get("matched_skills", [])
            if matched_skills and matched_skills != [""]:
                st.text(f"🎯 Matched Skills: {', '.join(matched_skills)}")

            cv_skills = result.get("cv_skills", [])
            if cv_skills and cv_skills != ["Unable to extract"]:
                with st.expander("CV Skills"):
                    st.write(", ".join(cv_skills))

            required_skills = result.get("required_skills", [])
            if required_skills and required_skills != ["Unable to extract"]:
                with st.expander("Required Skills"):
                    st.write(", ".join(required_skills))

        elif agent_name == "experience":
            if "cv_experience_years" in result:
                st.text(
                    f"📅 CV Experience: {result.get('cv_experience_years', 'N/A')}"
                )
                st.text(
                    f"📅 Required: {result.get('required_experience_years', 'N/A')}"
                )
                st.text(f"📊 CV Level: {result.get('cv_level', 'N/A')}")
                st.text(
                    f"📊 Required Level: {result.get('required_level', 'N/A')}"
                )

        elif agent_name == "preferences":
            if "work_style_match" in result:
                st.text(
                    f"🤝 Work Style Match: {result.get('work_style_match', 'N/A')}"
                )
                if (
                    result.get("cv_preferences", "Not specified")
                    != "Not specified"
                ):
                    st.text(
                        f"👤 CV Preferences: {result.get('cv_preferences')}"
                    )
                if (
                    result.get("job_culture", "Not specified")
                    != "Not specified"
                ):
                    st.text(f"🏢 Job Culture: {result.get('job_culture')}")

        elif agent_name == "semantic":
            if "embedding_similarity" in result:
                embedding_sim = result.get("embedding_similarity", 0.0)
                st.text(
                    f"🧠 Embedding Similarity: {format_score(embedding_sim)}"
                )
                st.text(
                    f"🎯 Contextual Fit: {result.get('contextual_fit', 'N/A')}"
                )
                st.text(
                    f"🏭 Industry Alignment: {result.get('industry_alignment', 'N/A')}"
                )
