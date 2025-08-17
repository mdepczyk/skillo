"""Matching process related exceptions."""


class MatchAnalysisError(Exception):
    """Failed to analyze match between CV and job posting."""

    def __init__(
        self,
        cv_filename: str = "",
        job_filename: str = "",
        original_error: str = "",
    ):
        message = f"Cannot analyze match between CV '{cv_filename}' and job '{job_filename}': {original_error}"
        super().__init__(message)


class ScoreCalculationError(Exception):
    """Failed to calculate weighted match score."""

    def __init__(self, missing_scores: str = "", original_error: str = ""):
        message = f"Cannot calculate final score, missing agent scores ({missing_scores}): {original_error}"
        super().__init__(message)


class PrefilteringError(Exception):
    """Failed to prefilter documents by similarity threshold."""

    def __init__(
        self,
        document_count: int = 0,
        similarity_threshold: float = 0.0,
        original_error: str = "",
    ):
        message = f"Cannot prefilter {document_count} documents with threshold {similarity_threshold}: {original_error}"
        super().__init__(message)


class StructuredDataMissingError(Exception):
    """Document lacks required structured data for matching."""

    def __init__(self, filename: str = "", document_type: str = ""):
        message = f"{document_type.upper()} '{filename}' is not processed - structured data missing for matching"
        super().__init__(message)


class MatchingConfigurationError(Exception):
    """Invalid matching configuration or parameters."""

    def __init__(
        self, parameter: str = "", value: str = "", expected: str = ""
    ):
        message = f"Invalid matching parameter '{parameter}' = '{value}', expected: {expected}"
        super().__init__(message)


class MatchingProcessError(Exception):
    """General matching process failed."""

    def __init__(self, process_type: str = "", original_error: str = ""):
        message = f"Matching process '{process_type}' failed: {original_error}"
        super().__init__(message)
