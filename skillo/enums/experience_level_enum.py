from enum import Enum


class ExperienceLevel(str, Enum):
    ENTRY = "Entry"
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    EXECUTIVE = "Executive"
    NOT_SPECIFIED = "Not specified"
