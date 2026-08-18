# Physical Intuition - Phase 7.45
# ===============================

"""
Canonical physical intuition contracts for Commonsense Reasoning.

Physical intuition evaluates:
- Gravity, containment, support, occlusion, collision
- Object permanence, stability
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# PHYSICAL INTUITION IDENTITY
# =============================================================================

@dataclass(frozen=True)
class PhysicalIntuitionIdentity:
    """
    Immutable identity for a physical intuition.
    """
    
    semantic_identity: str                    # Stable identity across runs
    context_hash: str                         # Hash of context that triggered this
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, context_hash: str) -> PhysicalIntuitionIdentity:
        """Create a new physical intuition identity."""
        return cls(
            semantic_identity=semantic_identity,
            context_hash=context_hash,
        )


# =============================================================================
# PHYSICAL CONSTRAINT
# =============================================================================

@dataclass(frozen=True)
class PhysicalConstraint:
    """
    A physical constraint inferred through intuition.
    
    Each constraint includes:
        - What is constrained
        - Why it's constrained (the inference basis)
        - Expected validity
        - Confidence estimate
    """
    
    constraint_id: str                        # Unique identifier
    affected_entity: str                      # e.g., "object_123"
    constraint_type: str                      # e.g., "cannot_fall_through", "must_be_supported"
    inferred_constraints: List[str] = field(default_factory=list)  # What does this mean?
    
    confidence: float = 0.5                   # Confidence in this inference
    
    @classmethod
    def create(
        cls,
        constraint_id: str,
        affected_entity: str,
        constraint_type: str,
        inferred_constraints: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> PhysicalConstraint:
        """Create a new physical constraint."""
        return cls(
            constraint_id=constraint_id,
            affected_entity=affected_entity,
            constraint_type=constraint_type,
            inferred_constraints=inferred_constraints or [],
            confidence=confidence,
        )


# =============================================================================
# PHYSICAL INTUITION MODEL
# =============================================================================

@dataclass(frozen=True)
class PhysicalIntuitionModel:
    """
    Model representing a physical intuition.
    
    Each model includes:
        - The inferred physical relationship
        - Supporting observations (visual, spatial, etc.)
        - Expected validity conditions
        - Confidence estimate
    
    Physical intuitions remain explicit and inspectable.
    """
    
    # Identity
    intuition_id: str                         # Unique intuition identifier
    semantic_identity: str                    # Semantic identity of this intuition type
    
    # Inferred relationship
    inferred_constraints: List[str] = field(default_factory=list)  # What is inferred?
    
    # Support
    supporting_observations: Tuple[str, ...] = field(default_factory=tuple)  # Visual/spatial evidence
    context_hash: str                         # Hash of context that triggered this
    
    # Validity and confidence
    expected_validity_conditions: List[str] = field(default_factory=list)
    confidence: float = 0.5
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        inferred_constraints: List[str],
        supporting_observations: Tuple[str, ...],
        context_hash: str,
        expected_validity_conditions: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> PhysicalIntuitionModel:
        """Create a new physical intuition model."""
        return cls(
            intuition_id=f"physical_intuition:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            inferred_constraints=inferred_constraints,
            supporting_observations=supporting_observations,
            context_hash=context_hash,
            expected_validity_conditions=expected_validity_conditions or [],
            confidence=confidence,
        )
    
    def get_constraint(self, constraint_type: str) -> Optional[str]:
        """Find a specific constraint by type."""
        for constraint in self.inferred_constraints:
            if constraint_type in constraint:
                return constraint
        return None


# =============================================================================
# PHYSICAL COMMONSENSE RECORD
# =============================================================================

@dataclass(frozen=True)
class PhysicalCommonsense:
    """
    Record of physical commonsense inference.
    
    Each record includes:
        - The physical intuition model itself
        - Contextual evaluation
        - Confidence assessment
        - Provenance tracking
    
    This is the primary contract for accessing physical intuitions during reasoning.
    """
    
    # Identity
    record_id: str                            # Unique record identifier
    semantic_identity: str                    # Semantic identity of this record
    
    # Physical data
    physical_intuition: PhysicalIntuitionModel  # The actual intuition
    
    # Evaluation
    context_compatible: bool = True           # Is current context compatible?
    
    # Confidence assessment
    effective_confidence: float = 0.5         # Final confidence after evaluation
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        physical_intuition: PhysicalIntuitionModel,
        context_compatible: bool,
        effective_confidence: float = 0.5,
    ) -> PhysicalCommonsense:
        """Create a new physical commonsense record."""
        return cls(
            record_id=f"physical_commonsense:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            physical_intuition=physical_intuition,
            context_compatible=context_compatible,
            effective_confidence=effective_confidence,
        )


# =============================================================================
# PHYSICAL INTUITION TYPES
# =============================================================================

class PhysicalIntuitionType(Enum):
    """Types of physical intuitions."""
    
    GRAVITY = "gravity"                       # Objects fall, need support
    CONTAINMENT = "containment"               # Containers hold contents
    SUPPORT = "support"                       # Objects resting on surfaces
    OCCLUSION = "occlusion"                   # Hidden objects still exist
    COLLISION = "collision"                   # Solid objects don't pass through
    OBJECT_PERMANENCE = "object_permanence"   # Unseen objects persist
    STABILITY = "stability"                   # Structures remain stable unless disturbed


# =============================================================================
# PHYSICAL TRACE
# =============================================================================

@dataclass(frozen=True)
class PhysicalTrace:
    """
    Complete trace of physical intuition through reasoning.
    
    A trace contains:
        - Original physical intuition model
        - All contexts it was applied in
        - Validation results
        - Confidence evolution
    """
    
    # Identity
    trace_id: str                             # Unique trace identifier
    
    # Physical data
    physical_intuition: PhysicalIntuitionModel  # The original intuition
    
    # Application history
    applications: List[Tuple[str, float]] = field(default_factory=list)  # (context_hash, confidence)
    
    # Validation history
    validations: List[Tuple[bool, Optional[str], float]] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, physical_intuition: PhysicalIntuitionModel) -> PhysicalTrace:
        """Create a new physical trace."""
        return cls(
            trace_id=f"physical_trace:{uuid.uuid4().hex[:16]}",
            physical_intuition=physical_intuition,
        )


__all__ = [
    "PhysicalIntuitionIdentity",
    "PhysicalConstraint",
    "PhysicalIntuitionModel",
    "PhysicalCommonsense",
    "PhysicalIntuitionType",
    "PhysicalTrace",
]