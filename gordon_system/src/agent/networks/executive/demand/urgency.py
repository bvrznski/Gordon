# Executive Demand Urgency Types
# ===============================

"""
Types for assessing demand urgency.

Urgency concerns time sensitivity; it may amplify demand but is distinct
from the demand itself.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveDemandUrgency:
    """
    Classes for executive demand urgency assessment.
    
    Urgency reflects unsafe continuation, deadlines, irreversible decisions,
    security requirements, rapidly propagating conflicts, or closing recovery
    windows. It does not grant authority.
    """
    
    NONE = "none"
    LOW = "low"
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    IMMEDIATE_REVIEW = "immediate_review"
    BLOCKING = "blocking"
    UNKNOWN = "unknown"

    @classmethod
    def all_classes(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveDemandUrgency",)