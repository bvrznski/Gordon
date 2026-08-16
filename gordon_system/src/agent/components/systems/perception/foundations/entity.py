# Perception Entity - Phase 5.2 Canonical Semantic Entity
# ========================================================

"""
Perception Entity: The fundamental semantic entity for all perceptual constructs.

Every PerceptualEntity possesses:
    - stable identity (PerceptionIdentity)
    - confidence level (0.0-1.0 belief in reliability)
    - uncertainty level (completely independent measure)
    - provenance record (origin tracking)
    - revision history (versioned evolution)

Entity Laws:
    ENTITY-LAW-001: Every entity has a stable semantic identity
    ENTITY-LAW-002: Every entity has confidence explicitly recorded
    ENTITY-LAW-003: Every entity has uncertainty explicitly recorded
    ENTITY-LAW-004: Confidence and uncertainty are independent measures
    ENTITY-LAW-005: Entity provenance is complete and preserved
    ENTITY-LAW-006: Entity revisions preserve history without overwriting
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, TYPE_CHECKING
from enum import Enum, auto
import time
import uuid

if TYPE_CHECKING:
    from .identity import PerceptionIdentity
    from .provenance import PerceptionProvenance


# =============================================================================
# ENTITY KINDS
# =============================================================================


class EntityKind(Enum):
    """
    Kinds of perceptual entities.
    
    Canonical hierarchy:
        OBSERVATION - Raw evidence from sensor
        SIGNAL      - Measured sensor output  
        FEATURE     - Structured property computed from signal
        PERCEPT     - Modality-independent representation
        SCENE       - Coherent collection of percepts
        EVENT       - Meaningful transition between states
    """
    
    OBSERVATION = "observation"     # Raw evidence from sensor
    SIGNAL = "signal"               # Measured sensor output
    FEATURE = "feature"             # Structured property computed from signal
    PERCEPT = "percept"             # Modality-independent representation
    SCENE = "scene"                 # Coherent collection of percepts
    EVENT = "event"                 # Meaningful transition between states


# =============================================================================
# ENTITY REVISION - Versioned evolution
# =============================================================================


@dataclass(frozen=True)
class EntityRevision:
    """
    A single revision in an entity's history.
    
    Revision tracks how an entity evolves over time while preserving
    its identity and provenance. Revisions are never overwritten;
    new revisions create new records that link to previous ones.
    
    Fields:
        revision_id:         Unique identifier for this revision
        version_number:      Sequential version number (1-indexed)
        timestamp_utc:       When this revision was created
        change_reason:       Why was this revision created?
        changed_by:          Who/what made the change (optional)
        previous_revision:   ID of immediately prior revision (optional)
    """
    
    revision_id: str                           # Unique revision identifier
    version_number: int                        # Sequential version number
    timestamp_utc: float                       # When created
    change_reason: Optional[str] = None        # Why was this created?
    changed_by: Optional[str] = None           # Who/what made the change?
    previous_revision: Optional[str] = None    # Prior revision ID


# =============================================================================
# PERCEPTUAL ENTITY - Base class for all perceptual constructs
# =============================================================================


@dataclass(frozen=True)
class PerceptualEntity:
    """
    Base class for all perceptual entities.
    
    Every entity possesses:
        - Identity: Stable semantic identifier
        - Confidence: Belief in reliability (0.0-1.0)
        - Uncertainty: Known limitations (completely independent)
        - Provenance: Complete origin tracking
        - Revision history: Versioned evolution
    
    Entity Laws:
        ENTITY-LAW-001: Every entity has a stable semantic identity
        ENTITY-LAW-002: Every entity has confidence explicitly recorded
        ENTITY-LAW-003: Every entity has uncertainty explicitly recorded
        ENTITY-LAW-004: Confidence and uncertainty are independent measures
        ENTITY-LAW-005: Entity provenance is complete and preserved
        ENTITY-LAW-006: Entity revisions preserve history without overwriting
    """
    
    # Identity (required) - import at runtime to avoid circular deps
    identity: Any            # Stable semantic identifier
    
    # Confidence & Uncertainty (required)
    confidence: float                          # 0.0 to 1.0 belief in reliability
    uncertainty: float                         # 0.0 to 1.0 known limitations
    
    # Provenance (required) - import at runtime to avoid circular deps
    provenance: Any         # Complete origin tracking
    
    # Revision history (optional - may be empty for initial revision)
    revision_history: Tuple[EntityRevision, ...] = field(default_factory=tuple)
    
    @property
    def entity_kind(self) -> EntityKind:
        """Get the kind of this entity from its identity."""
        return EntityKind(self.identity.entity_kind_str)
    
    @property
    def current_revision(self) -> int:
        """Get the current revision number."""
        return self.identity.current_revision
    
    @property
    def is_valid(self) -> bool:
        """Check if entity passes validation."""
        return validate_entity(self)
    
    def for_new_revision(
        self,
        new_confidence: Optional[float] = None,
        new_uncertainty: Optional[float] = None,
        change_reason: str = "New revision",
        changed_by: Optional[str] = None,
    ) -> PerceptualEntity:
        """
        Create a new revision of this entity.
        
        This preserves the identity but creates a new revision record
        and links it to the previous revision history.
        
        Args:
            new_confidence: New confidence value (optional, keeps current if None)
            new_uncertainty: New uncertainty value (optional, keeps current if None)
            change_reason: Why was this revision created?
            changed_by: Who/what made the change?
            
        Returns:
            New PerceptualEntity with updated revision
        """
        # Create new identity with incremented revision
        new_identity = self.identity.for_new_revision(
            f"{self.confidence}:{self.uncertainty}"
        )
        
        # Create new revision record
        new_revision = EntityRevision(
            revision_id=str(uuid.uuid4()),
            version_number=new_identity.current_revision,
            timestamp_utc=time.time(),
            change_reason=change_reason,
            changed_by=changed_by,
            previous_revision=self.identity.revision_identity,
        )
        
        # Update provenance with the revision
        from .provenance import dataclass_replace_provenance
        
        new_provenance = dataclass_replace_provenance(
            self.provenance,
            change_reason=f"{change_reason}: {new_revision.version_number}",
            changed_by=changed_by,
            semantic_time_utc=time.time(),
        )
        
        return dataclass_replace(
            self,
            identity=new_identity,
            confidence=new_confidence or self.confidence,
            uncertainty=new_uncertainty or self.uncertainty,
            provenance=new_provenance,
            revision_history=self.revision_history + (new_revision,),
        )


# =============================================================================
# PERCEPTUAL ENTITY BUILDER
# =============================================================================


class PerceptualEntityBuilder:
    """
    Mutable builder for constructing perceptual entities.
    
    Usage:
        entity = (PerceptualEntityBuilder()
            .set_identity(identity)
            .set_confidence(0.95)
            .set_uncertainty(0.02)
            .set_provenance(provenance)
            .build())
    """
    
    def __init__(self):
        self._identity: Optional["PerceptionIdentity"] = None
        self._confidence: float = 1.0
        self._uncertainty: float = 0.0
        self._provenance: Optional["PerceptionProvenance"] = None
        self._revision_history: List[EntityRevision] = []
    
    def set_identity(self, identity: "PerceptionIdentity") -> "PerceptualEntityBuilder":
        """Set the entity identity."""
        self._identity = identity
        return self
    
    def set_confidence(self, confidence: float) -> "PerceptualEntityBuilder":
        """Set confidence level (0.0-1.0)."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "PerceptualEntityBuilder":
        """Set uncertainty level (0.0-1.0)."""
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._uncertainty = uncertainty
        return self
    
    def set_provenance(self, provenance: "PerceptionProvenance") -> "PerceptualEntityBuilder":
        """Set the provenance record."""
        self._provenance = provenance
        return self
    
    def add_revision(self, revision: EntityRevision) -> "PerceptualEntityBuilder":
        """Add a revision to history."""
        self._revision_history.append(revision)
        return self
    
    def build(self) -> PerceptualEntity:
        """
        Build an immutable PerceptualEntity.
        
        Returns:
            New PerceptualEntity with all settings applied
            
        Raises:
            ValueError: If required fields are missing
        """
        if self._identity is None:
            raise ValueError("identity is required")
        if self._provenance is None:
            self._provenance = PerceptionProvenance(origin="system")
        
        return PerceptualEntity(
            identity=self._identity,
            confidence=self._confidence,
            uncertainty=self._uncertainty,
            provenance=self._provenance,
            revision_history=tuple(self._revision_history),
        )


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_entity(entity: PerceptualEntity) -> bool:
    """
    Validate a perceptual entity.
    
    Validation checks:
        - Entity has valid identity
        - Confidence is in range [0.0, 1.0]
        - Uncertainty is in range [0.0, 1.0]
        - Provenance is complete
        - Revision history is consistent
    
    Args:
        entity: The entity to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check identity exists and is valid
    if not entity.identity.entity_id:
        return False
    
    # Check confidence range
    if not 0.0 <= entity.confidence <= 1.0:
        return False
    
    # Check uncertainty range
    if not 0.0 <= entity.uncertainty <= 1.0:
        return False
    
    # Check provenance completeness
    if not hasattr(entity.provenance, "origin") or len(entity.provenance.origin) == 0:
        return False
    
    return True


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: PerceptualEntity, **kwargs) -> PerceptualEntity:
    """Replace fields in a frozen dataclass."""
    return PerceptualEntity(
        identity=kwargs.get("identity", instance.identity),
        confidence=kwargs.get("confidence", instance.confidence),
        uncertainty=kwargs.get("uncertainty", instance.uncertainty),
        provenance=kwargs.get("provenance", instance.provenance),
        revision_history=kwargs.get("revision_history", instance.revision_history),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    "EntityKind",
    "EntityRevision",
    "PerceptualEntity",
    "PerceptualEntityBuilder",
    "validate_entity",
    "dataclass_replace",
]