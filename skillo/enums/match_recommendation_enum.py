from enum import Enum


class MatchRecommendation(str, Enum):
    STRONG_MATCH = "Strong Match"
    GOOD_MATCH = "Good Match"
    FAIR_MATCH = "Fair Match"
    POOR_MATCH = "Poor Match"
    NO_MATCH = "No Match"
