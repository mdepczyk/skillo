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


class ExperienceLevel(str, Enum):
    """Experience levels."""

    ENTRY = "Entry"
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    EXECUTIVE = "Executive"
    NOT_SPECIFIED = "Not specified"


class RemoteWorkStatus(str, Enum):
    """Remote work status."""

    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"
    YES = "Yes"
    NO = "No"
    NOT_SPECIFIED = "Not specified"


class CommuteFeasibility(str, Enum):
    """Commute feasibility."""

    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"
    VERY_POOR = "Very Poor"


class ContextualFit(str, Enum):
    """Contextual fit."""

    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"


class IndustryAlignment(str, Enum):
    """Industry alignment."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class WorkStyleMatch(str, Enum):
    """Work style compatibility."""

    COMPATIBLE = "Compatible"
    PARTIALLY_COMPATIBLE = "Partially Compatible"
    NOT_COMPATIBLE = "Not Compatible"


class EducationLevel(str, Enum):
    """Education levels."""

    HIGHSCHOOL = "High School"
    ASSOCIATE = "Associate Degree"
    BACHELOR = "Bachelor's Degree"
    MASTER = "Master's Degree"
    DOCTORATE = "Doctorate/PhD"
    NOT_SPECIFIED = "Not specified"


class EducationMatch(str, Enum):
    """Education match levels."""

    EXCEEDS = "Exceeds Requirements"
    MEETS = "Meets Requirements"
    PARTIALLY_MEETS = "Partially Meets"
    BELOW_REQUIREMENTS = "Below Requirements"
