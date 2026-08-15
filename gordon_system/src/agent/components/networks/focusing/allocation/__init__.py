# Allocation Module - Focusing Network
# =====================================

"""
Resource allocation recommendations for focus candidates.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class AllocationRecommendation:
    """Allocation recommendation for a candidate."""
    
    candidate_id: str
    resource_budget: float = 0.0
    bandwidth_allocation: int = 1
    priority_boost: bool = False
    
    @classmethod
    def create_default(cls, candidate_id: str) -> "AllocationRecommendation":
        """Create a default allocation recommendation."""
        return cls(candidate_id=candidate_id)


@dataclass(frozen=True)
class AllocationState:
    """Allocation state for tracking resource assignments."""
    
    total_budget_used: float = 0.0
    candidates_allocated: int = 0
    
    @classmethod
    def create_initial(cls) -> "AllocationState":
        """Create initial allocation state."""
        return cls()