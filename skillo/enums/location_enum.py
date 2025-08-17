from enum import Enum


class CommuteFeasibility(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"
    VERY_POOR = "Very Poor"


class RemoteWorkStatus(str, Enum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"
    YES = "Yes"
    NO = "No"
    NOT_SPECIFIED = "Not specified"
