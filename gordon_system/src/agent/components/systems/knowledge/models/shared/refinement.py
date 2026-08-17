# Knowledge Model Refinement - Phase 6.7
# ======================================

"""
Model Refinement: Track how models evolve through new evidence and improved structure.

Models evolve without changing identity, preserving revision history while allowing
semantic improvements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REFINEMENT REASON - Why a model was refined
# =============================================================================


class RefinementReason(Enum):
    """
    Reasons for model refinement.
    
    Each refinement shall have an explicit reason indicating the cause of change.
    """
    
    NEW_EVIDENCE = "new_evidence"           # New evidence changed understanding
    IMPROVED_ASSUMPTIONS = "improved_assumptions"  # Better assumptions
    BETTER_CAUSAL_STRUCTURE = "better_causal_structure"  # Improved causal model
    NEW_CONCEPTS = "new_concepts"           # Added concepts
    UPDATED_RELATIONS = "updated_relations"   # Modified relations


# =============================================================================
# MODEL REFINEMENT - Canonical refinement record
# =============================================================================


@dataclass(frozen=True)
class ModelRefinement:
    """
    Canonical representation of model refinement in Gordon's knowledge system.
    
    Refinements track how models evolve while preserving identity and history.
    
    Fields:
        refinement_identity:   Unique identifier for this refinement event
        previous_revision:     ID of the previous model revision
        refined_revision:      ID of the new refined model revision
        refinement_reason:     Why the refinement occurred
        affected_components:   Which components were modified
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    refinement_identity: str            # Unique ID for this refinement event
    
    # Revision tracking (required)
    previous_revision: str              # Previous model revision ID
    refined_revision: str               # New refined revision ID
    
    # Refinement cause (required)
    refinement_reason: RefinementReason = RefinementReason.NEW_EVIDENCE
    
    # Affected components
    affected_components: Tuple[str, ...] = field(default_factory=tuple)  # Component IDs
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_evolutionary(self) -> bool:
        """Check if this refinement maintains semantic identity."""
        return self.refinement_reason in (
            RefinementReason.NEW_EVIDENCE,
            RefinementReason.IMPROVED_ASSUMPTIONS,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert refinement to dictionary for serialization."""
        return {
            "refinement_identity": self.refinement_identity,
            "previous_revision": self.previous_revision,
            "refined_revision": self.refined_revision,
            "refinement_reason": self.refinement_reason.value if self.refinement_reason else None,
            "affected_components": list(self.affected_components),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelRefinement":
        """Create refinement from dictionary."""
        reason_value = data.get("refinement_reason", "new_evidence")
        try:
            refinement_reason = RefinementReason(reason_value)
        except ValueError:
            refinement_reason = RefinementReason.NEW_EVIDENCE
        
        return cls(
            refinement_identity=data.get("refinement_identity", str(uuid.uuid4())),
            previous_revision=data.get("previous_revision", ""),
            refined_revision=data.get("refined_revision", ""),
            refinement_reason=refinement_reason,
            affected_components=tuple(data.get("affected_components", [])),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        previous_revision: str,
        refined_revision: str,
        reason: RefinementReason = RefinementReason.NEW_EVIDENCE,
        affected_components: Optional[List[str]] = None,
    ) -> "ModelRefinement":
        """
        Create a new model refinement record.
        
        Args:
            previous_revision: ID of the previous revision
            refined_revision: ID of the new refined revision
            reason: Why the refinement occurred
            affected_components: List of affected component IDs (optional)
            
        Returns:
            A new refinement record
        """
        return cls(
            refinement_identity=f"refinement:{uuid.uuid4().hex[:16]}",
            previous_revision=previous_revision,
            refined_revision=refined_revision,
            refinement_reason=reason,
            affected_components=tuple(affected_components or []),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def add_affected_component(
        self,
        component_id: str,
    ) -> "ModelRefinement":
        """Create a revision with an additional affected component."""
        if component_id in self.affected_components:
            return self
        return ModelRefinement(
            refinement_identity=self.refinement_identity,
            previous_revision=self.previous_revision,
            refined_revision=self.refined_revision,
            refinement_reason=self.refinement_reason,
            affected_components=self.affected_components + (component_id,),
            provenance={
                **self.provenance,
                "component_added": component_id,
                "revised_at_utc": time.time(),
            },
        )


# =============================================================================
# REFINEMENT TRACKER
# =============================================================================


class RefinementTracker:
    """
    Tracks and validates model refinements.
    
    Ensures refinements preserve revision lineage and identity stability.
    """
    
    def __init__(
        self,
        require_revision_chain: bool = True,
    ):
        """
        Initialize the tracker.
        
        Args:
            require_revision_chain: Whether to enforce revision chain validity
        """
        self._require_chain = require_revision_chain
    
    def track_refinement(
        self,
        previous_model_id: str,
        new_model_id: str,
        reason: RefinementReason,
        affected_components: List[str],
    ) -> ModelRefinement:
        """
        Record a model refinement.
        
        Args:
            previous_model_id: ID of the model before refinement
            new_model_id: ID of the model after refinement
            reason: Why the refinement occurred
            affected_components: List of affected component IDs
            
        Returns:
            A refinement record
        """
        return ModelRefinement.create(
            previous_revision=previous_model_id,
            refined_revision=new_model_id,
            reason=reason,
            affected_components=affected_components,
        )
    
    def validate_refinement_chain(
        self,
        refinements: List[ModelRefinement],
    ) -> Tuple[bool, List[str]]:
        """
        Validate a chain of refinements.
        
        Ensures each refinement connects to the previous one.
        
        Args:
            refinements: List of refinements in chronological order
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if len(refinements) == 0:
            return True, issues
        
        for i in range(1, len(refinements)):
            prev = refinements[i - 1]
            curr = refinements[i]
            
            # Check that current's previous matches previous refinement's refined
            if curr.previous_revision != prev.refined_revision:
                issues.append(
                    f"Refinement chain broken at position {i}: "
                    f"{curr.previous_revision} != {prev.refined_revision}"
                )
        
        return len(issues) == 0, issues


__all__ = [
    "RefinementReason",
    "ModelRefinement",
    "RefinementTracker",
]