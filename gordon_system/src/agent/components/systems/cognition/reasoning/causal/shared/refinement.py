# Causal Refinement - Phase 7.5
# =============================

"""
Canonical Causal Refinement.

Mechanism models evolve through new observations, experiments,
and validated interventions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class RefinementChange:
    """
    A single change made during model refinement.
    
    Documents what changed and why.
    """
    
    # Identity
    change_id: str                      # Unique change identifier
    
    # Change type
    change_type: str                    # e.g., "add_edge", "remove_node", "modify_equation"
    
    # What was changed
    target_element: str                 # The element that was modified
    previous_value: Optional[str] = None  # Before the change
    new_value: Optional[str] = None     # After the change
    
    # Reason for change
    reason: str                         # Why was this change made?
    
    # Evidence supporting the change
    evidence: Tuple[str, ...] = ()      # Supporting observations/experiments


@dataclass(frozen=True)
class CausalRefinement:
    """
    A refinement of a causal model with complete history.
    
    Identity remains stable while content evolves.
    """
    
    # Identity
    refinement_id: str                  # Unique refinement identifier
    
    # Previous model state
    previous_model: Any                 # Previous version (can be any type)
    
    # Refined model state
    refined_model: Any                  # New version after refinement
    
    # Changes made
    supporting_changes: Tuple[RefinementChange, ...]  # All changes applied
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    reason_for_refinement: str = ""     # Why was refinement needed?
    
    @property
    def change_count(self) -> int:
        """Number of changes in this refinement."""
        return len(self.supporting_changes)
    
    def get_changes_by_type(self, change_type: str) -> Tuple[RefinementChange, ...]:
        """Get all changes of a specific type."""
        return tuple(c for c in self.supporting_changes if c.change_type == change_type)


@dataclass(frozen=True)
class RefinementPipeline:
    """
    A complete refinement pipeline with all stages.
    
    From model evaluation to final refinement.
    """
    
    # Identity
    pipeline_id: str                    # Unique pipeline identifier
    
    # Stages
    initial_model: Any                  # Starting model
    evaluation_results: Tuple[str, ...]  # Issues found
    refinement_actions: Tuple[RefinementChange, ...]  # Changes applied
    final_model: Any                    # Resulting model
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None


def make_refinement(
    previous_model: Any,
    refined_model: Any,
    changes: List[RefinementChange],
    reason_for_refinement: str = "",
) -> CausalRefinement:
    """Create a new refinement."""
    return CausalRefinement(
        refinement_id=f"refinement:{uuid.uuid4().hex[:16]}",
        previous_model=previous_model,
        refined_model=refined_model,
        supporting_changes=tuple(changes),
        reason_for_refinement=reason_for_refinement,
    )


__all__ = [
    "RefinementChange",
    "CausalRefinement",
    "RefinementPipeline",
]