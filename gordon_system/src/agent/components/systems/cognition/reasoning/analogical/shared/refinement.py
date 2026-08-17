# Analogy Refinement - Phase 7.4
# ============================

"""
Canonical Analogy Refinement Contract.

Refinement evolves mappings based on new evidence and feedback.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AnalogyRefinement:
    """
    A refinement of a previous mapping.
    
    Mappings evolve through:
        - New evidence
        - Additional cases
        - Failed transfers (what didn't work?)
        - Constraint discovery
        - Better schemas
    
    Identity remains stable during refinement.
    """
    
    # Identity
    refinement_id: str                        # Unique identifier
    
    # What's being refined
    previous_mapping_id: str                  # Original mapping ID
    refined_mapping_id: str                   # New mapping ID
    
    # Refinement details
    refinement_type: str = "adjustment"       # e.g., "adjustment", "expansion"
    
    # Supporting changes (what changed and why?)
    supporting_changes: Tuple[Dict[str, Any], ...] = ()
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def change_count(self) -> int:
        """Number of supporting changes."""
        return len(self.supporting_changes)
    
    @classmethod
    def create(
        cls,
        previous_mapping_id: str,
        refined_mapping_id: str,
        refinement_type: str = "adjustment",
        changes: Optional[List[Dict[str, Any]]] = None,
    ) -> AnalogyRefinement:
        """Create a new refinement."""
        return cls(
            refinement_id=f"analogy_refinement:{uuid.uuid4().hex[:16]}",
            previous_mapping_id=previous_mapping_id,
            refined_mapping_id=refined_mapping_id,
            refinement_type=refinement_type,
            supporting_changes=tuple(changes or []),
        )
    
    def add_change(self, change: Dict[str, Any]) -> AnalogyRefinement:
        """Add a supporting change."""
        return dataclass_replace(
            self,
            supporting_changes=self.supporting_changes + (change,),
        )


@dataclass(frozen=True)
class RefinementHistory:
    """
    Complete history of refinements to an analogy.
    
    Used for traceability and debugging.
    """
    
    # Identity
    history_id: str                           # Unique identifier
    
    # Original mapping
    original_mapping_id: str                  # Starting point
    
    # All refinements in order
    refinements: Tuple[AnalogyRefinement, ...] = ()
    
    # Final state
    is_completed: bool = False                # Has refinement converged?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def refinement_count(self) -> int:
        """Number of refinements in history."""
        return len(self.refinements)
    
    @classmethod
    def create(cls, original_mapping_id: str) -> RefinementHistory:
        """Create a new refinement history."""
        return cls(
            history_id=f"refinement_history:{uuid.uuid4().hex[:16]}",
            original_mapping_id=original_mapping_id,
        )
    
    def add_refinement(self, refinement: AnalogyRefinement) -> RefinementHistory:
        """Add a refinement to the history."""
        return dataclass_replace(
            self,
            refinements=self.refinements + (refinement,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AnalogyRefinement",
    "RefinementHistory",
]