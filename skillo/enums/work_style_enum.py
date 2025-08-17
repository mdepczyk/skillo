from enum import Enum


class WorkStyleMatch(str, Enum):
    COMPATIBLE = "Compatible"
    PARTIALLY_COMPATIBLE = "Partially Compatible"
    NOT_COMPATIBLE = "Not Compatible"
