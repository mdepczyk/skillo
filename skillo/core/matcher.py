"""Core job matching functionality using multi-agent system."""

from typing import Any, Dict, List

import streamlit as st

from skillo.agents import (
    LangChainCVProcessingAgent,
    LangChainJobProcessingAgent,
    LangChainNormalizationAgent,
    LangChainSupervisorAgent,
)
from skillo.config import Config
from skillo.core.vectorstore import VectorStore
from skillo.exceptions import (
    DocumentProcessingError,
    DocumentRetrievalError,
    MatchingProcessError,
    PrefilteringError,
)
from skillo.utils.logger import logger


class JobMatcher:
    """Main job matcher class that handles CV-to-job matching operations."""

    def __init__(self, config: Config = None):
        """
        Initialize job matcher.

        Args:
            config: Configuration instance
        """
        self.config = config or Config()
        self.vector_store = VectorStore(self.config)
        self.supervisor = LangChainSupervisorAgent(
            self.config, vectorstore=self.vector_store
        )
        self.cv_processor = LangChainCVProcessingAgent()
        self.job_processor = LangChainJobProcessingAgent()
        self.normalizer = LangChainNormalizationAgent()

    def _prefilter_by_similarity(
        self,
        candidate_profile: str,
        documents: List[Dict[str, Any]],
        target_field: str,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Pre-filter documents by cosine similarity between candidate profile and target field.

        Args:
            candidate_profile: Candidate's profile text
            documents: List of documents to filter
            target_field: Field name to compare against (e.g., 'job_title', 'profile')
            similarity_threshold: Minimum similarity score (default 0.7)

        Returns:
            Filtered and sorted documents by similarity
        """
        try:
            similarities = []

            for doc in documents:
                structured_data = doc.get("structured_data", {})
                sections = structured_data.get("sections", {})

                if target_field == "job_title":
                    target_content = sections.get("job_title", "")
                elif target_field == "profile":
                    target_content = structured_data.get("profile", "")
                else:
                    target_content = sections.get(target_field, "")

                if not target_content:
                    similarity = 0.0
                else:
                    similarity = (
                        self.vector_store.calculate_semantic_similarity(
                            candidate_profile, target_content
                        )
                    )

                similarities.append(
                    {"document": doc, "similarity": similarity}
                )

            filtered = [
                item
                for item in similarities
                if item["similarity"] >= similarity_threshold
            ]

            filtered.sort(key=lambda x: x["similarity"], reverse=True)

            return [item["document"] for item in filtered]

        except Exception as e:
            raise PrefilteringError(
                len(documents), similarity_threshold, str(e)
            )

    def match_cv_to_all_jobs(
        self, cv_document: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Match a CV against all available job postings.

        Args:
            cv_document: CV document dictionary

        Returns:
            List of match results sorted by score

        Raises:
            MatchingError: If matching process fails
        """
        try:
            job_documents = self.vector_store.get_all_documents_for_matching(
                doc_type="job"
            )

            if not job_documents:
                st.warning("No job postings found in database")
                return []

            cv_structured = cv_document.get("structured_data", {})
            cv_profile = cv_structured.get("profile", "")

            if cv_profile:
                st.info(
                    f"🔍 Pre-filtering {len(job_documents)} jobs by profile similarity."
                )
                logger.info(
                    "MATCHER",
                    f"Pre-filtering {len(job_documents)} jobs by profile similarity",
                    f"CV Profile: {cv_profile}...",
                )

                filtered_jobs = self._prefilter_by_similarity(
                    candidate_profile=cv_profile,
                    documents=job_documents,
                    target_field="job_title",
                    similarity_threshold=0.7,
                )

                st.success(
                    f"✅ Found {len(filtered_jobs)} jobs with high profile similarity"
                )
                logger.success(
                    "MATCHER",
                    f"Found {len(filtered_jobs)} jobs with high profile similarity",
                )
                job_documents = filtered_jobs

            if not job_documents:
                st.warning("No jobs passed similarity pre-filtering")
                return []

            matches = []
            processed_count = 0

            for job_doc in job_documents:
                if len(matches) >= self.config.TOP_CANDIDATES_COUNT:
                    st.info(
                        f"🛑 Reached max candidates ({self.config.TOP_CANDIDATES_COUNT}), stopping analysis"
                    )
                    break

                processed_count += 1
                try:
                    cv_structured = cv_document.get("structured_data")
                    job_structured = job_doc.get("structured_data")

                    if not cv_structured:
                        st.error(
                            f"CV {cv_document['metadata']['filename']} is not processed. Please process with Document Processing Agent first!"
                        )
                        continue

                    if not job_structured:
                        st.error(
                            f"Job {job_doc['metadata']['filename']} is not processed. Please process with Document Processing Agent first!"
                        )
                        continue

                    match_result = (
                        self.supervisor.analyze_match_with_structured_data(
                            cv_structured=cv_structured,
                            job_structured=job_structured,
                        )
                    )

                    job_structured_data = job_doc.get("structured_data", {})
                    match_result["job_info"] = {
                        "id": job_doc["id"],
                        "filename": job_doc["metadata"]["filename"],
                        "file_path": job_doc["metadata"]["file_path"],
                        "company": job_structured_data.get("company", "Unknown Company"),
                        "job_title": job_structured_data.get("job_title", "Unknown Position"),
                    }

                    cv_structured_data = cv_document.get("structured_data", {})
                    match_result["cv_info"] = {
                        "id": cv_document["id"],
                        "filename": cv_document["metadata"]["filename"],
                        "name": cv_structured_data.get("name", "Unknown"),
                        "profile": cv_structured_data.get("profile", "Unknown"),
                    }

                    matches.append(match_result)

                except Exception as e:
                    st.warning(
                        f"Failed to match CV with job {job_doc['metadata']['filename']}: {str(e)}"
                    )
                    continue

            matches.sort(key=lambda x: x["weighted_final_score"], reverse=True)

            filtered_matches = [
                m
                for m in matches
                if m["weighted_final_score"] >= self.config.MIN_MATCH_SCORE
            ]

            return filtered_matches[: self.config.TOP_CANDIDATES_COUNT]

        except DocumentRetrievalError as e:
            raise MatchingProcessError("job matching", str(e)) from e

        except Exception as e:
            raise MatchingProcessError("job matching", str(e)) from e

    def match_job_to_all_cvs(
        self, job_document: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Match a job posting against all available CVs.

        Args:
            job_document: Job document dictionary

        Returns:
            List of match results sorted by score

        Raises:
            MatchingError: If matching process fails
        """
        try:
            cv_documents = self.vector_store.get_all_documents_for_matching(
                doc_type="cv"
            )

            if not cv_documents:
                st.warning("No CVs found in database")
                return []

            job_structured = job_document.get("structured_data", {})
            job_sections = job_structured.get("sections", {})
            job_title = job_sections.get("job_title", "")

            if job_title:
                st.info(
                    f"🔍 Pre-filtering {len(cv_documents)} CVs by profile similarity..."
                )
                filtered_cvs = self._prefilter_by_similarity(
                    candidate_profile=job_title,
                    documents=cv_documents,
                    target_field="profile",
                    similarity_threshold=0.7,
                )
                st.success(
                    f"✅ Found {len(filtered_cvs)} CVs with high profile similarity"
                )
                cv_documents = filtered_cvs

            if not cv_documents:
                st.warning("No CVs passed similarity pre-filtering")
                return []

            matches = []
            processed_count = 0
            for cv_doc in cv_documents:
                if len(matches) >= self.config.TOP_CANDIDATES_COUNT:
                    st.info(
                        f"🛑 Reached max candidates ({self.config.TOP_CANDIDATES_COUNT}), stopping analysis"
                    )
                    break

                processed_count += 1
                try:
                    cv_structured = cv_doc.get("structured_data")
                    job_structured = job_document.get("structured_data")

                    if not cv_structured:
                        st.error(
                            f"CV {cv_doc['metadata']['filename']} is not processed. Please process with Document Processing Agent first!"
                        )
                        continue

                    if not job_structured:
                        st.error(
                            f"Job {job_document['metadata']['filename']} is not processed. Please process with Document Processing Agent first!"
                        )
                        continue

                    match_result = (
                        self.supervisor.analyze_match_with_structured_data(
                            cv_structured=cv_structured,
                            job_structured=job_structured,
                        )
                    )

                    cv_structured_data = cv_doc.get("structured_data", {})
                    match_result["cv_info"] = {
                        "id": cv_doc["id"],
                        "filename": cv_doc["metadata"]["filename"],
                        "file_path": cv_doc["metadata"]["file_path"],
                        "name": cv_structured_data.get("name", "Unknown"),
                        "profile": cv_structured_data.get("profile", "Unknown"),
                    }

                    job_structured_data = job_document.get("structured_data", {})
                    match_result["job_info"] = {
                        "id": job_document["id"],
                        "filename": job_document["metadata"]["filename"],
                        "company": job_structured_data.get("company", "Unknown Company"),
                        "job_title": job_structured_data.get("job_title", "Unknown Position"),
                    }

                    matches.append(match_result)

                except Exception as e:
                    st.warning(
                        f"Failed to match job with CV {cv_doc['metadata']['filename']}: {str(e)}"
                    )
                    continue

            matches.sort(key=lambda x: x["weighted_final_score"], reverse=True)

            filtered_matches = [
                m
                for m in matches
                if m["weighted_final_score"] >= self.config.MIN_MATCH_SCORE
            ]

            return filtered_matches[: self.config.TOP_CANDIDATES_COUNT]

        except DocumentRetrievalError as e:
            raise MatchingProcessError("candidate matching", str(e)) from e

        except Exception as e:
            raise MatchingProcessError("candidate matching", str(e)) from e

    def process_cv_document(
        self, cv_content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process CV document using Document Processing and Normalization agents.

        Args:
            cv_content: Raw CV text content
            metadata: Document metadata

        Returns:
            Processed and normalized CV data

        Raises:
            MatchingError: If processing fails
        """
        try:
            st.info("Processing CV with specialized agents...")

            structured_cv = self.cv_processor.process_cv(cv_content)

            normalized_cv = self.normalizer.normalize_cv_data(structured_cv)

            processed_document = {
                "content": cv_content,
                "structured_data": structured_cv,
                "normalized_data": normalized_cv,
                "metadata": metadata,
                "document_type": "cv",
            }

            st.success("✅ CV processing completed successfully")
            return processed_document

        except Exception as e:
            raise DocumentProcessingError("cv", "", str(e)) from e

    def process_job_document(
        self, job_content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process job posting document using Document Processing and Normalization agents.

        Args:
            job_content: Raw job posting text content
            metadata: Document metadata

        Returns:
            Processed and normalized job data

        Raises:
            MatchingError: If processing fails
        """
        try:
            st.info("Processing job posting with specialized agents...")

            structured_job = self.job_processor.process_job_posting(
                job_content
            )

            normalized_job = self.normalizer.normalize_job_data(structured_job)

            processed_document = {
                "content": job_content,
                "structured_data": structured_job,
                "normalized_data": normalized_job,
                "metadata": metadata,
                "document_type": "job",
            }

            st.success("✅ Job posting processing completed successfully")
            return processed_document

        except Exception as e:
            raise DocumentProcessingError("job", "", str(e)) from e
