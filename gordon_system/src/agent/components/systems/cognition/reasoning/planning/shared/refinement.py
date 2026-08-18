# Plan Refinement - Phase 7.20
# ===========================

"""
Canonical Plan Refinement contracts for Phase 7.20.

Plans evolve through new constraints, resource changes, environment changes,
decision revisions, and execution feedback while preserving identity.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class PlanningRefinement:
    """
    Record of a plan refinement event.
    
    Refinements occur when:
        - New constraints are discovered
        - Resources change availability
        - Environment changes
        - Decision is revised
        - Execution feedback arrives
    
    The original identity remains stable, but the refined plan may differ.
    """
    
    # Identity
    refinement_id: str                        # Unique refinement identifier
    
    # Previous version
    previous_plan: Tuple[str, ...] = ()       # Previous plan state (serialized)
    
    # Refined version
    refined_plan: Tuple[str, ...] = ()        # New plan after refinement
    
    # Refinement strategy
    refinement_strategy: str = "default"      # How was it refined?
    
    # Trigger for refinement
    refinement_trigger: Optional[str] = None  # What triggered the change?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        previous_plan: Tuple[str, ...],
        refined_plan: Tuple[str, ...],
        refinement_strategy: str = "default",
        refinement_trigger: Optional[str] = None,
    ) -> PlanningRefinement:
        """Create a new plan refinement record."""
        return cls(
            refinement_id=f"refinement:{uuid.uuid4().hex[:16]}",
            previous_plan=previous_plan,
            refined_plan=refined_plan,
            refinement_strategy=refinement_strategy,
            refinement_trigger=refinement_trigger,
        )


@dataclass(frozen=True)
class PlanHistory:
    """
    Complete history of a plan's refinements.
    
    Each refinement preserves the previous version, creating an audit trail.
    """
    
    # Identity
    history_id: str                           # Unique history identifier
    
    # Original plan identity (stable across all versions)
    original_plan_identity: str               # Root identity
    
    # All versions in order (oldest first)
    plan_versions: Tuple[PlanningRefinement, ...] = ()
    
    # Current state
    current_version_number: int = 1           # How many refinements?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    last_updated_utc: float = field(default_factory=time.time)
    
    @property
    def version_count(self) -> int:
        """Count total versions in history."""
        return len(self.plan_versions) + 1  # +1 for original
    
    @classmethod
    def create(
        cls,
        original_plan_identity: str,
    ) -> PlanHistory:
        """Create a new plan history."""
        return cls(
            history_id=f"planhistory:{uuid.uuid4().hex[:16]}",
            original_plan_identity=original_plan_identity,
        )
    
    def with_refinement(self, refinement: PlanningRefinement) -> PlanHistory:
        """Add a refinement to the history."""
        new_versions = self.plan_versions + (refinement,)
        return dataclass_replace(
            self,
            plan_versions=new_versions,
            current_version_number=len(new_versions) + 1,
            last_updated_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PlanningRefinement",
    "PlanHistory",
]