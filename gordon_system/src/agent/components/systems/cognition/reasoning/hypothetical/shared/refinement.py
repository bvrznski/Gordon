# Hypothesis Refinement - Phase 7.15 Part 2
# ===========================================

"""
Canonical Hypothesis Refinement Contract.

Refinement evaluates supporting evidence, new assumptions, constraint updates,
merged hypotheses, split hypotheses, and generalization.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class RefinementIdentity:
    """
    Immutable identity for a refinement operation.
    
    Allows tracking refinements across sessions.
    """
    
    semantic_identity: str                    # Stable identity across runs
    
    @classmethod
    def create(cls, semantic_identity: str) -> RefinementIdentity:
        """Create a new refinement identity."""
        return cls(semantic_identity=semantic_identity)


@dataclass(frozen=True)
class HypothesisRefinement:
    """
    Record of hypothesis refinement.
    
    Tracks how hypotheses evolve through new evidence, assumptions,
    and constraints while preserving original identity.
    """
    
    # Identity
    refinement_id: str                        # Unique identifier
    
    # Previous state
    previous_hypothesis_id: str               # ID of hypothesis before refinement
    
    # Refined state
    refined_hypothesis_id: str                # ID after refinement (same semantic identity)
    
    # Changes made
    supporting_changes: Tuple[str, ...] = ()  # Supporting evidence/changes
    assumption_updates: Tuple[str, ...] = ()  # New or updated assumptions
    
    # Refinement strategy
    refinement_strategy: str = "evidence_based"  # How was it refined?
    
    # Metadata
    refined_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        previous_hypothesis_id: str,
        refined_hypothesis_id: str,
        supporting_changes: Optional[List[str]] = None,
        assumption_updates: Optional[List[str]] = None,
        refinement_strategy: str = "evidence_based",
    ) -> HypothesisRefinement:
        """Create a new refinement record."""
        return cls(
            refinement_id=f"refinement:{uuid.uuid4().hex[:16]}",
            previous_hypothesis_id=previous_hypothesis_id,
            refined_hypothesis_id=refined_hypothesis_id,
            supporting_changes=tuple(supporting_changes or []),
            assumption_updates=tuple(assumption_updates or []),
            refinement_strategy=refinement_strategy,
        )


@dataclass(frozen=True)
class HypothesisRefinementPipeline:
    """
    Pipeline of refinements applied to hypotheses.
    
    Tracks the complete chain of refinements from original hypothesis
    to final form.
    """
    
    # Identity
    pipeline_id: str                          # Unique identifier
    
    # Initial and final states
    initial_hypotheses: Tuple[RefinementIdentity, ...]  # Starting points
    refined_hypotheses: Tuple[RefinementIdentity, ...]  # Final forms
    
    # Refinements applied
    refinement_steps: Tuple[HypothesisRefinement, ...] = ()  # All refinements
    
    # Pipeline metadata
    refinement_strategy: str = "default"      # Overall strategy
    
    # Metadata
    pipeline_started_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_refinements(self) -> int:
        """Return number of refinement steps."""
        return len(self.refinement_steps)
    
    @classmethod
    def create(
        cls,
        initial_hypotheses: List[RefinementIdentity],
        refined_hypotheses: List[RefinementIdentity],
        refinement_steps: Optional[List[HypothesisRefinement]] = None,
        refinement_strategy: str = "default",
    ) -> HypothesisRefinementPipeline:
        """Create a new refinement pipeline."""
        return cls(
            pipeline_id=f"refinement_pipeline:{uuid.uuid4().hex[:16]}",
            initial_hypotheses=tuple(initial_hypotheses),
            refined_hypotheses=tuple(refined_hypotheses),
            refinement_steps=tuple(refinement_steps or []),
            refinement_strategy=refinement_strategy,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RefinementIdentity",
    "HypothesisRefinement",
    "HypothesisRefinementPipeline",
]