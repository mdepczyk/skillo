from typing import Protocol, Dict, Any


class MatchingEvents(Protocol):
    """Protocol defining events that can occur during matching process."""
    
    def on_no_documents_found(self, doc_type: str) -> None:
        """Called when no documents found in database."""
        ...
    
    def on_prefiltering_started(self, count: int, doc_type: str) -> None:
        """Called when similarity pre-filtering starts."""
        ...
    
    def on_documents_found(self, count: int, doc_type: str) -> None:
        """Called when documents are successfully retrieved."""
        ...
    
    def on_no_matches_after_prefiltering(self, doc_type: str) -> None:
        """Called when no documents pass similarity threshold."""
        ...
    
    def on_matching_started(self, cv_name: str, job_info: str) -> None:
        """Called when starting to match specific CV-job pair."""
        ...
    
    def on_matching_error(self, error_msg: str, context: str) -> None:
        """Called when matching process encounters an error."""
        ...
    
    def on_match_completed(self, result: Dict[str, Any]) -> None:
        """Called when single match is completed successfully."""
        ...
    
    def on_max_candidates_reached(self, max_count: int) -> None:
        """Called when maximum candidate limit is reached."""
        ...
    
    def on_document_not_processed(self, filename: str, doc_type: str) -> None:
        """Called when document lacks required structured data."""
        ...