from typing import Any, Dict, List

from skillo.agents import LangChainSupervisorAgent
from skillo.config import Config
from skillo.core.vectorstore import VectorStore
from skillo.core.events import MatchingEvents
from skillo.exceptions.exceptions import SkilloMatchingError, SkilloStorageError
from skillo.utils.logger import logger


class JobMatcher:
    """Main job matcher class that handles CV-to-job matching operations."""

    def __init__(self, config: Config, events: MatchingEvents):
        """
        Initialize job matcher.

        Args:
            config: Configuration instance
            events: Event handler for notifications (required)
        """
        self.config = config
        self.vector_store = VectorStore(self.config)
        self.supervisor = LangChainSupervisorAgent(
            self.config, vectorstore=self.vector_store
        )
        self.events = events

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
        return self._generic_match(
            source_document=cv_document,
            target_doc_type="job",
            profile_extractor=self._extract_cv_profile,
            target_field="job_title",
            info_extractor=self._extract_job_info,
        )

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
        return self._generic_match(
            source_document=job_document,
            target_doc_type="cv",
            profile_extractor=self._extract_job_profile,
            target_field="profile",
            info_extractor=self._extract_cv_info,
        )

    def _generic_match(
        self,
        source_document: Dict[str, Any],
        target_doc_type: str,
        profile_extractor: callable,
        target_field: str,
        info_extractor: callable,
    ) -> List[Dict[str, Any]]:
        """
        Generic matching method implementing template pattern.
        
        Args:
            source_document: Document to match from
            target_doc_type: Type of documents to match against ('cv' or 'job')
            profile_extractor: Function to extract profile from source document
            target_field: Field to use for similarity filtering 
            info_extractor: Function to extract info for match result
            
        Returns:
            List of match results sorted by score
        """
        try:
            target_documents = self.vector_store.get_all_documents_for_matching(
                doc_type=target_doc_type
            )

            if not target_documents:
                self.events.on_no_documents_found(target_doc_type)
                return []

            profile = profile_extractor(source_document)

            if profile:
                self.events.on_prefiltering_started(len(target_documents), target_doc_type)
                logger.info(
                    "MATCHER",
                    f"Pre-filtering {len(target_documents)} {target_doc_type}s by profile similarity",
                    f"Profile: {profile[:100]}...",
                )

                filtered_documents = self._prefilter_by_similarity(
                    candidate_profile=profile,
                    documents=target_documents,
                    target_field=target_field,
                    similarity_threshold=0.7,
                )

                self.events.on_documents_found(len(filtered_documents), target_doc_type)
                target_documents = filtered_documents

            if not target_documents:
                self.events.on_no_matches_after_prefiltering(target_doc_type)
                return []

            matches = []
            for target_doc in target_documents:
                if len(matches) >= self.config.TOP_CANDIDATES_COUNT:
                    self.events.on_max_candidates_reached(self.config.TOP_CANDIDATES_COUNT)
                    break

                try:
                    source_structured = source_document.get("structured_data")
                    target_structured = target_doc.get("structured_data")

                    if not source_structured:
                        source_doc_type = "cv" if target_doc_type == "job" else "job"
                        self.events.on_document_not_processed(
                            source_document['metadata']['filename'], source_doc_type
                        )
                        continue

                    if not target_structured:
                        self.events.on_document_not_processed(
                            target_doc['metadata']['filename'], target_doc_type
                        )
                        continue

                    if target_doc_type == "job":
                        cv_name = source_structured.get("name", "Unknown")
                        job_title = target_structured.get("job_title", "Unknown Position")
                        self.events.on_matching_started(cv_name, job_title)
                        
                        match_result = self.supervisor.analyze_match_with_structured_data(
                            cv_structured=source_structured,
                            job_structured=target_structured,
                        )
                    else:
                        job_name = source_structured.get("job_title", "Unknown Position")
                        cv_name = target_structured.get("name", "Unknown")
                        self.events.on_matching_started(cv_name, job_name)
                        
                        match_result = self.supervisor.analyze_match_with_structured_data(
                            cv_structured=target_structured,
                            job_structured=source_structured,
                        )

                    match_result[f"{target_doc_type}_info"] = info_extractor(target_doc)

                    if target_doc_type == "job":
                        cv_structured_data = source_document.get("structured_data", {})
                        match_result["cv_info"] = {
                            "id": source_document["id"],
                            "filename": source_document["metadata"]["filename"],
                            "name": cv_structured_data.get("name", "Unknown"),
                            "profile": cv_structured_data.get("profile", "Unknown"),
                        }
                    else:
                        job_structured_data = source_document.get("structured_data", {})
                        match_result["job_info"] = {
                            "id": source_document["id"],
                            "filename": source_document["metadata"]["filename"],
                            "company": job_structured_data.get("company", "Unknown Company"),
                            "job_title": job_structured_data.get("job_title", "Unknown Position"),
                        }

                    matches.append(match_result)

                except Exception as e:
                    context = f"Failed to match {source_document['metadata']['filename']} with {target_doc_type} {target_doc['metadata']['filename']}"
                    self.events.on_matching_error(str(e), context)
                    continue

            matches.sort(key=lambda x: x["weighted_final_score"], reverse=True)

            filtered_matches = [
                match
                for match in matches
                if match["weighted_final_score"] >= self.config.MIN_MATCH_SCORE
            ]

            final_matches = filtered_matches[: self.config.TOP_CANDIDATES_COUNT]
            
            if final_matches:
                best_match = final_matches[0]
                self.events.on_match_completed({
                    "total_matches": len(final_matches),
                    "best_score": best_match["weighted_final_score"],
                    "weighted_final_score": best_match["weighted_final_score"]
                })
            
            return final_matches

        except SkilloStorageError as e:
            raise SkilloMatchingError(f"{target_doc_type} matching failed: {str(e)}") from e

        except Exception as e:
            raise SkilloMatchingError(f"{target_doc_type} matching failed: {str(e)}") from e

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
                    similarity = self.vector_store.calculate_semantic_similarity(
                        candidate_profile, target_content
                    )

                similarities.append({
                    "document": doc, 
                    "similarity": similarity
                })

            filtered = [
                item for item in similarities 
                if item["similarity"] >= similarity_threshold
            ]
            
            filtered.sort(key=lambda x: x["similarity"], reverse=True)
            
            return [item["document"] for item in filtered]

        except Exception as e:
            raise SkilloMatchingError(f"Prefiltering failed: {str(e)}")

    def _extract_cv_profile(self, cv_doc: Dict[str, Any]) -> str:
        """Extract profile from CV document."""
        return cv_doc.get("structured_data", {}).get("profile", "")

    def _extract_job_profile(self, job_doc: Dict[str, Any]) -> str:
        """Extract profile from job document."""
        job_sections = job_doc.get("structured_data", {}).get("sections", {})
        return job_sections.get("job_title", "")

    def _extract_job_info(self, job_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Extract job info for match result."""
        job_structured_data = job_doc.get("structured_data", {})
        return {
            "id": job_doc["id"],
            "filename": job_doc["metadata"]["filename"],
            "file_path": job_doc["metadata"]["file_path"],
            "company": job_structured_data.get("company", "Unknown Company"),
            "job_title": job_structured_data.get("job_title", "Unknown Position"),
        }

    def _extract_cv_info(self, cv_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Extract CV info for match result."""
        cv_structured_data = cv_doc.get("structured_data", {})
        return {
            "id": cv_doc["id"],
            "filename": cv_doc["metadata"]["filename"],
            "name": cv_structured_data.get("name", "Unknown"),
            "profile": cv_structured_data.get("profile", "Unknown"),
        }

