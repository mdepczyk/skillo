from enum import Enum


class ContextualFit(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"


class IndustryAlignment(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
