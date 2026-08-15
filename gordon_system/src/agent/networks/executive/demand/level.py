# Executive Demand Level Types
# =============================

"""
Types for representing demand levels.

Demand level is typed and bounded.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveDemandLevel:
    """
    Typed demand levels for executive assessments.
    
    SATURATED means required demand appears to exceed safe or available
    executive control under supplied projections. It does not imply
    runtime resource saturation.
    """
    
    NONE = "none"
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"
    SATURATED = "saturated"
    UNKNOWN = "unknown"

    @classmethod
    def all_levels(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveDemandLevel",)