# Executive Interference Assessment Types
# =======================================

"""
Types for assessing interference between executive structures.

Interference concerns the degree to which one active semantic structure
impairs another, even without a direct conflict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveInterferenceClass:
    """
    Interference classes for executive conflicts.
    """
    
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    BLOCKING = "blocking"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveInterferenceAssessment:
    """
    Structured assessment of executive interference.
    """
    
    goal_interference_class: str = "none"
    rule_interference_class: str = "none"
    response_interference_class: str = "none"
    action_interference_class: str = "none"
    memory_interference_class: str = "none"
    focus_interference_class: str = "none"
    strategy_interference_class: str = "none"
    communication_interference_class: str = "none"
    temporal_interference_class: str = "none"
    authority_interference_class: str = "none"
    total_interference_class: str = "none"


__all__: Tuple[str, ...] = (
    "ExecutiveInterferenceClass",
    "ExecutiveInterferenceAssessment",
)