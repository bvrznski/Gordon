# Explanation Refinement - Phase 7.14
# ====================================

"""
Explanation refinement for explanatory reasoning.

Explanation models evolve through:
    - New evidence
    - Improved reasoning
    - Better organization
    - Clarified assumptions
    - Updated conclusions
    
Identity remains stable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class RefinementIdentity:
    """
    Immutable identity for an explanation refinement process.
    """
    
    semantic_identity: str                    # Stable identity across runs
    refinement_number: int = 1                # For repeated refinements
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, refinement_number: int = 1) -> RefinementIdentity:
        """Create a new refinement identity."""
        return cls(
            semantic_identity=semantic_identity,
            refinement_number=refinement_number,
        )


@dataclass(frozen=True)
class ExplanationRefinement:
    """
    Refinement process for an explanation.
    
    Explanation models evolve through new evidence, improved reasoning,
    better organization, clarified assumptions, and updated conclusions
    while maintaining stable identity.
    """
    
    # Identity
    refinement_id: str                        # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Previous state
    previous_explanation: Dict[str, Any]      # What was there before?
    
    # Refined state
    refined_explanation: Dict[str, Any]       # What changed?
    
    # Supporting changes (what caused the refinement?)
    supporting_changes: Tuple[Dict[str, Any], ...]
    
    # Process tracking
    change_count: int = 0                     # Number of changes
    improvement_score: float = 0.0            # How much better?
    
    @property
    def is_significant(self) -> bool:
        """Check if refinement is significant."""
        return self.improvement_score > 0.1
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        previous_explanation: Dict[str, Any],
        refined_explanation: Dict[str, Any],
        supporting_changes: List[Dict[str, Any]],
    ) -> "ExplanationRefinement":
        """Create a new refinement record."""
        changes = tuple(supporting_changes)
        
        # Calculate improvement (simplified)
        prev_score = previous_explanation.get("quality_score", 0.5)
        refined_score = refined_explanation.get("quality_score", 0.5)
        improvement = max(0.0, refined_score - prev_score)
        
        return cls(
            refinement_id=f"refinement:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            previous_explanation=previous_explanation,
            refined_explanation=refined_explanation,
            supporting_changes=changes,
            change_count=len(changes),
            improvement_score=improvement,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RefinementIdentity",
    "ExplanationRefinement",
]