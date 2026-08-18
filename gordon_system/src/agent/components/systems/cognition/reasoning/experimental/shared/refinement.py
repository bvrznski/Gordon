# Experimental Reasoning - Refinement
# ====================================

"""
Canonical Refinement contracts.

Experiment designs evolve through new evidence and improvements while preserving identity.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ExperimentalRefinement:
    """
    A refinement of an experiment design.
    
    Experiments evolve through:
        - Better interventions
        - New observations
        - Improved measurements
        - Resource changes
        - Updated hypotheses
    
    Identity remains stable across refinements.
    """
    
    # Identity
    refinement_id: str                          # Unique identifier for this refinement
    original_experiment_identity: str           # Original experiment identity (preserved)
    
    # Refinement context
    previous_design: Dict[str, Any] = field(default_factory=dict)  # Design before refinement
    refined_design: Dict[str, Any] = field(default_factory=dict)   # Design after refinement
    
    # Supporting changes
    supporting_changes: Tuple[str, ...] = ()    # What changed and why?
    
    # Refinement rationale
    rationale: str = ""                         # Why was this refinement made?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did refinement originate?
    
    @property
    def refinement_type(self) -> str:
        """Determine the type of refinement based on changes."""
        if not self.previous_design or not self.refined_design:
            return "initial"
        
        changes = set(self.refined_design.keys()) - set(self.previous_design.keys())
        removed = set(self.previous_design.keys()) - set(self.refined_design.keys())
        
        if changes and not removed:
            return "additive"
        elif removed and not changes:
            return "subtractive"
        elif changes and removed:
            return "substitutive"
        else:
            return "update"
    
    @classmethod
    def create(
        cls,
        original_experiment_identity: str,
        previous_design: Optional[Dict[str, Any]] = None,
        refined_design: Optional[Dict[str, Any]] = None,
        origin_context: str = "unknown",
    ) -> ExperimentalRefinement:
        """Create a new experimental refinement."""
        return cls(
            refinement_id=f"refinement:{uuid.uuid4().hex[:16]}",
            original_experiment_identity=original_experiment_identity,
            previous_design=previous_design or {},
            refined_design=refined_design or {},
            origin_context=origin_context,
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if refinement has been fully applied."""
        return len(self.supporting_changes) > 0


@dataclass(frozen=True)
class RefinementHistory:
    """
    Complete history of refinements for an experiment.
    
    Allows reconstruction of how an experiment evolved over time.
    """
    
    # Identity
    history_id: str                             # Unique identifier
    experiment_identity: str                    # Original experiment identity
    
    # Refinement chain
    refinements: Tuple[ExperimentalRefinement, ...]
    
    @property
    def refinement_count(self) -> int:
        """Get the number of refinements in the history."""
        return len(self.refinements)
    
    @property
    def is_ancestral(self) -> bool:
        """Check if this is an ancestral (original) experiment with no refinements."""
        return len(self.refinements) == 0
    
    def get_refinement_at_step(self, step: int) -> Optional[ExperimentalRefinement]:
        """Get the refinement at a specific position in history."""
        if 0 <= step < len(self.refinements):
            return self.refinements[step]
        return None
    
    @classmethod
    def create(
        cls,
        experiment_identity: str,
        refinements: List[ExperimentalRefinement] = None,
    ) -> RefinementHistory:
        """Create a new refinement history."""
        return cls(
            history_id=f"refinement_history:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            refinements=tuple(refinements or []),
        )


__all__ = [
    "ExperimentalRefinement",
    "RefinementHistory",
]