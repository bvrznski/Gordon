# Executive Conflict Dimension Types
# ===================================

"""
Types for representing conflict dimensions - semantic aspects along which
a conflict may be assessed.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveConflictDimension:
    """
    Dimensions along which a conflict may be assessed.
    
    A single conflict may span multiple dimensions.
    """
    
    LOGICAL = "logical"
    SEMANTIC = "semantic"
    FACTUAL = "factual"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    GOAL = "goal"
    COMMITMENT = "commitment"
    PRIORITY = "priority"
    STRATEGIC = "strategic"
    POLICY = "policy"
    SECURITY = "security"
    AUTHORITY = "authority"
    RESOURCE = "resource"
    CAPABILITY = "capability"
    ATTENTIONAL = "attentional"
    MOTIVATIONAL = "motivational"
    DECISIONAL = "decisional"
    BEHAVIORAL = "behavioral"
    COMMUNICATION = "communication"
    PRIVACY = "privacy"
    DISCLOSURE = "disclosure"
    COMPLETION = "completion"
    RECOVERY = "recovery"
    DEPENDENCY = "dependency"
    UNKNOWN = "unknown"

    @classmethod
    def all_dimensions(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveConflictDimension",)