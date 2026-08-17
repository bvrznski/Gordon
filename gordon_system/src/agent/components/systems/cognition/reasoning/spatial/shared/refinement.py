# Spatial Refinement - Phase 7.9
# =============================

"""
Canonical Spatial Refinement.

Spatial models evolve through new observations, better localization,
updated geometry, environment changes, and map refinement.
Identity remains stable throughout refinements.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class RefinementChange:
    """
    Individual change made during model refinement.
    
    Each change documents what was modified and why.
    """
    
    # Identity
    change_id: str                          # Unique identifier
    
    # What changed
    entity_id: str                          # Which entity?
    property_name: str                      # Which property?
    
    # Old and new values
    old_value: Optional[Any] = None         # Previous value (if any)
    new_value: Any                          # New value
    
    # Why it changed
    change_reason: str = ""                 # Human-readable reason
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""


@dataclass(frozen=True)
class SpatialRefinement:
    """
    Result of spatial model refinement.
    
    Refinements preserve identity while updating the model.
    """
    
    # Identity - remains stable
    refinement_id: str                      # Unique identifier
    
    # Model before refinement
    previous_model_semantic_identity: str   # Same semantic identity as before
    
    # Model after refinement
    refined_model_semantic_identity: str    # Same semantic identity as before
    
    # Changes made
    changes: Tuple[RefinementChange, ...] = ()
    
    # Refinement metadata
    change_count: int = 0                   # Number of changes
    
    # Validation after refinement
    post_refinement_valid: bool = True      # Is refined model valid?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def is_improvement(self) -> bool:
        """Check if refinement improved the model."""
        return self.change_count > 0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        previous_model_semantic: str,
    ) -> SpatialRefinement:
        """Create a new refinement record."""
        return cls(
            refinement_id=f"refinement:{uuid.uuid4().hex[:16]}",
            previous_model_semantic_identity=previous_model_semantic,
            refined_model_semantic_identity=semantic_identity,
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def add_change(self, change: RefinementChange) -> SpatialRefinement:
        """Return new refinement with additional change."""
        return dataclass_replace(
            self,
            changes=self.changes + (change,),
            change_count=self.change_count + 1,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialRefinement", 
    "RefinementChange",
]