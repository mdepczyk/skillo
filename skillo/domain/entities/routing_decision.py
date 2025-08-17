from dataclasses import dataclass
from typing import List


@dataclass
class RoutingDecision:
    """Decision from AgentRouter about which agents to invoke."""

    agents: List[str]
    reasoning: str
    confidence: float
    priority: str = "normal"
