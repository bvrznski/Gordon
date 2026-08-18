# Negotiation Set - Phase 7.42
# =============================

"""
Canonical Negotiation Set.

A negotiation set defines the immutable context for a negotiation session.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StakeholderReference:
    """
    Reference to a stakeholder in the negotiation.
    
    Contains minimal identifying information without full stakeholder model.
    """
    
    stakeholder_identity: str          # Unique identifier for the stakeholder
    stakeholder_name: str              # Display name
    authority_level: Optional[str] = None  # Authority level (optional)


@dataclass(frozen=True)
class ConstraintDefinition:
    """
    A constraint that must be satisfied in the negotiation.
    
    Constraints define hard limits that cannot be compromised.
    """
    
    constraint_identity: str           # Unique identifier
    constraint_type: str               # Type of constraint (e.g., "legal", "technical")
    constraint_text: str               # The actual constraint statement
    is_mandatory: bool = True          # Must be satisfied or negotiation fails


@dataclass(frozen=True)
class NegotiationSet:
    """
    Immutable set defining the context for a negotiation session.
    
    A negotiation set contains:
        - Identity of the negotiation
        - List of participating stakeholders
        - Constraints that must be satisfied
        - Agreement requirements
    
    The negotiation set remains immutable during reasoning to ensure
    reproducibility and traceability.
    """
    
    # Identity
    negotiation_set_identity: str          # Unique identifier for this set
    semantic_identity: str                 # Stable identity across runs
    
    # Stakeholders
    stakeholders: Tuple[StakeholderReference, ...]  # All participating stakeholders
    
    # Constraints
    constraints: Tuple[ConstraintDefinition, ...]   # Mandatory constraints
    
    # Agreement requirements
    agreement_requirements: Tuple[str, ...] = ()    # What makes an agreement valid?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    version: int = 1                               # Set version for evolution tracking
    
    @property
    def stakeholder_count(self) -> int:
        """Number of stakeholders in the negotiation."""
        return len(self.stakeholders)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        stakeholders: List[StakeholderReference],
        constraints: Optional[List[ConstraintDefinition]] = None,
        agreement_requirements: Optional[List[str]] = None,
    ) -> NegotiationSet:
        """Create a new negotiation set."""
        return cls(
            negotiation_set_identity=f"negotiation-set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            stakeholders=tuple(stakeholders),
            constraints=tuple(constraints or []),
            agreement_requirements=tuple(agreement_requirements or []),
        )
    
    def with_stakeholder(self, stakeholder: StakeholderReference) -> NegotiationSet:
        """Return a new set with an additional stakeholder."""
        return dataclass_replace(
            self,
            stakeholders=self.stakeholders + (stakeholder,),
            version=self.version + 1,
        )
    
    def without_stakeholder(self, identity: str) -> NegotiationSet:
        """Return a new set without the specified stakeholder."""
        filtered = tuple(s for s in self.stakeholders if s.stakeholder_identity != identity)
        return dataclass_replace(
            self,
            stakeholders=filtered,
            version=self.version + 1,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "NegotiationSet",
    "StakeholderReference", 
    "ConstraintDefinition",
]
