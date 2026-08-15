# Bias Module - Focusing Network
# ===============================

"""
Bias-related computations for focus candidates.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class BiasAssessment:
    """Bias assessment for a candidate."""
    
    candidate_id: str
    bias_strength: float = 0.0
    bias_type: str = "none"
    
    @classmethod
    def create_no_bias(cls, candidate_id: str) -> "BiasAssessment":
        """Create an assessment with no bias detected."""
        return cls(candidate_id=candidate_id)


@dataclass(frozen=True)
class BiasState:
    """Bias state for tracking detected biases."""
    
    bias_count: int = 0
    max_bias_strength: float = 0.0
    
    @classmethod
    def create_initial(cls) -> "BiasState":
        """Create initial bias state."""
        return cls()