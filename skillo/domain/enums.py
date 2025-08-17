from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration."""

    CV = "cv"
    JOB = "job"


class MatchRecommendation(str, Enum):
    """Match recommendation levels."""

    STRONG_MATCH = "Strong Match"
    GOOD_MATCH = "Good Match"
    FAIR_MATCH = "Fair Match"
    POOR_MATCH = "Poor Match"
    NO_MATCH = "No Match"
