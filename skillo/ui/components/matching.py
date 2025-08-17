from typing import Any, Dict, List

import streamlit as st

from skillo.application.dto import MatchResultDto, UiHelpers


class MatchResultsDisplay:
    """Match results display component."""

    @staticmethod
    def display_job_matches(matches: List[MatchResultDto]) -> None:
        """Display job matches."""
        for i, match in enumerate(matches, 1):
            company = match.job_metadata.get("contact", "Unknown Company")
            job_title = match.job_metadata.get("job_title", "Unknown Position")
            job_display = f"{company} - {job_title}"

            with st.expander(
                f"#{i} {job_display} - Score: {UiHelpers.format_score(match.weighted_final_score)}"
            ):
                MatchResultsDisplay._render_match_details(match, f"job_{i}")

    @staticmethod
    def display_candidate_matches(matches: List[MatchResultDto]) -> None:
        """Display candidate matches."""
        for i, match in enumerate(matches, 1):
            name = match.cv_metadata.get("name", "Unknown")
            profile = match.cv_metadata.get("job_title", "Unknown Position")
            candidate_display = f"{name} - {profile}"

            with st.expander(
                f"#{i} {candidate_display} - Score: {UiHelpers.format_score(match.weighted_final_score)}"
            ):
                MatchResultsDisplay._render_match_details(
                    match, f"candidate_{i}"
                )

    @staticmethod
    def _render_match_details(match: MatchResultDto, unique_key: str) -> None:
        """Render match details."""

        col1, col2 = st.columns([1, 3])

        with col1:
            MatchResultsDisplay._render_scores_section(match)

        with col2:
            MatchResultsDisplay._render_summary_section(match, unique_key)

    @staticmethod
    def _render_scores_section(match: MatchResultDto) -> None:
        """Render final score and individual agent scores."""

        final_score = match.weighted_final_score
        match_category = match.recommendation

        st.metric(
            "Final Score",
            UiHelpers.format_score(final_score),
            delta=f"{match_category}",
        )

        st.markdown("**Agent Scores**")

        agent_scores = {
            "Skills": match.agent_scores.get("skills", 0),
            "Location": match.agent_scores.get("location", 0),
            "Experience": match.agent_scores.get("experience", 0),
            "Preferences": match.agent_scores.get("preferences", 0),
            "Education": match.agent_scores.get("education", 0),
        }

        for agent_name, score in agent_scores.items():
            st.metric(agent_name, UiHelpers.format_score(score))

    @staticmethod
    def _render_summary_section(
        match: MatchResultDto, unique_key: str
    ) -> None:
        """Render detailed agent analysis directly."""
        st.markdown("**Detailed Agent Analysis**")

        MatchResultsDisplay._display_detailed_analysis(
            match.detailed_results, unique_key
        )

    @staticmethod
    def _display_detailed_analysis(
        agent_results: Dict[str, Any], unique_key: str
    ) -> None:
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
    ) -> None:
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

        elif agent_name == "education":
            if "cv_degree" in result:
                st.text(f"🎓 CV Degree: {result.get('cv_degree', 'N/A')}")
                st.text(
                    f"🎓 Required Degree: {result.get('required_degree', 'N/A')}"
                )
                st.text(f"📚 CV Field: {result.get('cv_field', 'N/A')}")
                st.text(
                    f"📚 Required Field: {result.get('required_field', 'N/A')}"
                )
                st.text(
                    f"🏆 Certifications: {result.get('certifications', 'N/A')}"
                )
                st.text(
                    f"✅ Degree Match: {result.get('degree_match', 'N/A')}"
                )
