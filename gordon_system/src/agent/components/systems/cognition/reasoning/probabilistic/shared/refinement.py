# Probability Model Refinement - Phase 7.7
# =========================================

"""
Canonical refinement contracts for probability models.

Models evolve through additional evidence, calibration, and validation.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class RefinementChange:
    """
    A specific change made during model refinement.
    
    Represents one modification to improve a probability model.
    """
    
    # Identity
    change_id: str                          # Unique identifier
    
    # Change type
    change_type: str = "prior_update"       # What kind of change?
    
    # Affected element
    affected_variable: str = ""             # Which variable/parameter changed?
    
    # Before and after
    before_value: Optional[float] = None    # Original value
    after_value: Optional[float] = None     # New value
    
    # Rationale
    justification: str = ""                 # Why was this change made?


@dataclass(frozen=True)
class ProbabilityModelRefinement:
    """
    Result of refining a probability model.
    
    Shows how a model improved through evidence, calibration, or validation.
    """
    
    # Identity
    refinement_id: str                      # Unique identifier
    
    # Original model reference
    previous_model_identity: str            # Which model was refined?
    
    # Changes made
    changes: Tuple[RefinementChange, ...] = ()
    
    # Refined model
    refined_model: Optional[str] = None     # Reference to new model
    
    # Quality improvement
    quality_improvement: float = 0.0        # How much better?
    
    # Metadata
    refined_at_utc: float = field(default_factory=time.time)
    
    @property
    def has_changes(self) -> bool:
        """Check if any changes were made."""
        return len(self.changes) > 0
    
    @classmethod
    def create_empty(cls, model_id: str) -> ProbabilityModelRefinement:
        """Create a refinement with no changes (model unchanged)."""
        return cls(
            refinement_id=f"refinement:{uuid.uuid4().hex[:16]}",
            previous_model_identity=model_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ProbabilityModelRefinement", 
    "RefinementChange",
]