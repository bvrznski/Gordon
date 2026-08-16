# Oriented Network Continuity Model - Phase 4.7.8 Part 1 & 2
# ===========================================================

"""
Continuity Model for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Continuity represents semantic identity across cognitive evolution
    - It never implies uninterrupted execution
    - Pure semantic representation only
    
PHASE 4.7.8 PART 1 - CONTINUITY TYPES:
    ContinuousOrientation
    InterruptedOrientation
    ResumedOrientation
    RestoredOrientation
    InheritedOrientation

PHASE 4.7.8 PART 2 - CONTRACTS:
    ContinuityReference, ContinuityRelationship, ContinuityRequirement,
    ContinuityAuthority, ContinuityOwner, ContinuityProjection
    
NO RUNTIME BEHAVIOR:
    - No runtime restoration
    - No scheduler state
    - No execution management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from gordon_system.src.agent.components.networks.oriented.persistence.base import (
    BasePersistenceModel,
    PersistenceIdentity,
)


# =============================================================================
# CONTINUITY STATE TYPES
# =============================================================================

@dataclass(frozen=True)
class ContinuousOrientation(BasePersistenceModel):
    """
    A continuous orientation with uninterrupted semantic identity.
    
    ARCHITECTURAL INVARIANTS:
        CO-INV-001: Continuity represents semantic identity across cognitive evolution
        CO-INV-002: Continuity never implies uninterrupted execution
        CO-INV-003: Continuity survives interruption when semantic identity remains valid
        CO-INV-004: Continuity survives suspension
        CO-INV-005: Continuity survives recovery
        
    NOT RESPONSIBLE FOR:
        - Runtime continuation (owned by runtime phases)
        - Execution restoration
        - Scheduler state
    """
    
    persistence_type: str = field(default="continuous", init=False)
    source_id: PersistenceIdentity = ""
    """The source identity when continuity is inherited"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        source_id: PersistenceIdentity = "",
        revision: int = 1,
        version: int = 1,
    ) -> ContinuousOrientation:
        return cls(
            persistence_id=persistence_id,
            source_id=source_id,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "source_id": self.source_id,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContinuousOrientation:
        return cls(
            persistence_id=data["persistence_id"],
            source_id=data.get("source_id", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        if self.source_id:
            return (self.source_id,)
        return ()


@dataclass(frozen=True)
class InterruptedOrientation(BasePersistenceModel):
    """
    An interrupted orientation - identity preserved across interruption.
    
    ARCHITECTURAL INVARIANTS:
        IO-INV-001: Interruption preserves semantic identity
        IO-INV-002: Interruption does not terminate Orientation
        
    SEMANTIC ROLE:
        Represents an orientation that has been interrupted but maintains identity.
        The interruption is a semantic state, not a runtime event.
    """
    
    persistence_type: str = field(default="interrupted", init=False)
    interruption_reason: str = ""
    """Semantic description of the interruption"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        interruption_reason: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> InterruptedOrientation:
        return cls(
            persistence_id=persistence_id,
            interruption_reason=interruption_reason,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "interruption_reason": self.interruption_reason,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InterruptedOrientation:
        return cls(
            persistence_id=data["persistence_id"],
            interruption_reason=data.get("interruption_reason", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "interruption_reason": self.interruption_reason,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ResumedOrientation(BasePersistenceModel):
    """
    A resumed orientation - restarted after interruption.
    
    ARCHITECTURAL INVARIANTS:
        RO-INV-001: Resumption restores semantic continuity
        RO-INV-002: Resumed identity is derived from interrupted state
        
    SEMANTIC ROLE:
        Represents an orientation that has been resumed after interruption.
    """
    
    persistence_type: str = field(default="resumed", init=False)
    original_id: PersistenceIdentity = ""
    """The ID of the interrupted orientation"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        original_id: PersistenceIdentity = "",
        revision: int = 1,
        version: int = 1,
    ) -> ResumedOrientation:
        return cls(
            persistence_id=persistence_id,
            original_id=original_id,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "original_id": self.original_id,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResumedOrientation:
        return cls(
            persistence_id=data["persistence_id"],
            original_id=data.get("original_id", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "original_id": self.original_id,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        if self.original_id:
            return (self.original_id,)
        return ()


@dataclass(frozen=True)
class RestoredOrientation(BasePersistenceModel):
    """
    A restored orientation - recovered from persistence state.
    
    ARCHITECTURAL INVARIANTS:
        RSO-INV-001: Restoration preserves semantic lineage
        RSO-INV-002: Restored identity is deterministically derived
        
    SEMANTIC ROLE:
        Represents an orientation that has been restored from persisted state.
    """
    
    persistence_type: str = field(default="restored", init=False)
    source_state_id: PersistenceIdentity = ""
    """The ID of the persisted state"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        source_state_id: PersistenceIdentity = "",
        revision: int = 1,
        version: int = 1,
    ) -> RestoredOrientation:
        return cls(
            persistence_id=persistence_id,
            source_state_id=source_state_id,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "source_state_id": self.source_state_id,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RestoredOrientation:
        return cls(
            persistence_id=data["persistence_id"],
            source_state_id=data.get("source_state_id", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "source_state_id": self.source_state_id,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        if self.source_state_id:
            return (self.source_state_id,)
        return ()


@dataclass(frozen=True)
class InheritedOrientation(BasePersistenceModel):
    """
    An inherited orientation - continuity from source.
    
    ARCHITECTURAL INVARIANTS:
        IO-INV-001: Inheritance preserves semantic lineage
        IO-INV-002: Inherited identity maintains provenance chain
        
    SEMANTIC ROLE:
        Represents an orientation that inherits semantic identity from a source.
    """
    
    persistence_type: str = field(default="inherited", init=False)
    inheritance_source: PersistenceIdentity = ""
    """The ID of the inheritance source"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        inheritance_source: PersistenceIdentity = "",
        revision: int = 1,
        version: int = 1,
    ) -> InheritedOrientation:
        return cls(
            persistence_id=persistence_id,
            inheritance_source=inheritance_source,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "inheritance_source": self.inheritance_source,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InheritedOrientation:
        return cls(
            persistence_id=data["persistence_id"],
            inheritance_source=data.get("inheritance_source", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "inheritance_source": self.inheritance_source,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        if self.inheritance_source:
            return (self.inheritance_source,)
        return ()


# =============================================================================
# CONTINUITY REFERENCE (Part 2 - Ownership Contract)
# =============================================================================

@dataclass(frozen=True)
class ContinuityReference:
    """
    Reference to a continuity state.
    
    OWNERSHIP CONTRACT (Part 2):
        CO-OWNERSHIP-LAW-001: Continuity owns semantic identity
        CO-OWNERSHIP-LAW-002: Continuity never owns runtime restoration
        
    INVARIANTS:
        CR-INV-001: Reference is immutable
        CR-INV-002: Reference never owns the referenced continuity
        CR-INV-003: Reference maintains identity across revisions
    """
    
    continuity_id: PersistenceIdentity
    """Reference to the continuity state"""
    
    revision: int = 1
    
    @classmethod
    def create(cls, continuity_id: PersistenceIdentity) -> ContinuityReference:
        return cls(continuity_id=continuity_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "continuity_id": self.continuity_id,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContinuityReference:
        return cls(
            continuity_id=data["continuity_id"],
            revision=data.get("revision", 1),
        )


@dataclass(frozen=True)
class ContinuityRelationship:
    """
    Semantic relationship between continuity states.
    
    OWNERSHIP CONTRACT (Part 2):
        CO-RELATIONSHIP-LAW-001: Relationship represents semantic connection only
        
    TYPES:
        CONTINUITY-RELATION-SOURCE: Source of continuity
        CONTINUITY-RELATION-TARGET: Target of continuity
        CONTINUITY-RELATION-INHERITANCE: Inherited continuity
        CONTINUITY-RELATION-INTERRUPTION: Interrupted continuity
        CONTINUITY-RELATION-RESUMPTION: Resumed continuity
    """
    
    source_id: PersistenceIdentity
    """Source continuity state"""
    
    target_id: PersistenceIdentity
    """Target continuity state"""
    
    relationship_type: str = ""
    """Type of relationship"""
    
    @classmethod
    def create(
        cls,
        source_id: PersistenceIdentity,
        target_id: PersistenceIdentity,
        relationship_type: str = "",
    ) -> ContinuityRelationship:
        return cls(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContinuityRelationship:
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=data.get("relationship_type", ""),
        )


@dataclass(frozen=True)
class ContinuityRequirement:
    """
    Semantic requirement for continuity.
    
    OWNERSHIP CONTRACT (Part 2):
        CO-REQUIREMENT-LAW-001: Requirement describes semantic expectations only
        
    TYPES:
        CONTINUITY-REQ-IDENTITY: Identity must be preserved
        CONTINUITY-REQ-CONTEXT: Context must be preserved
        CONTINUITY-REQ-GOAL: Goal must be preserved
        CONTINUITY-REQ-TASK: Task must be preserved
        CONTINUITY-REQ-STATE: State must be preserved
    """
    
    requirement_type: str = ""
    """Type of continuity requirement"""
    
    condition: str = ""
    """Semantic condition for the requirement"""
    
    @classmethod
    def create(cls, requirement_type: str, condition: str = "") -> ContinuityRequirement:
        return cls(requirement_type=requirement_type, condition=condition)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_type": self.requirement_type,
            "condition": self.condition,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContinuityRequirement:
        return cls(
            requirement_type=data["requirement_type"],
            condition=data.get("condition", ""),
        )


@dataclass(frozen=True)
class ContinuityAuthority:
    """
    Authority specification for continuity.
    
    OWNERSHIP CONTRACT (Part 2):
        CO-AUTHORITY-LAW-001: Authority remains externally defined
    """
    
    authority_id: str = ""
    """Identifier of the authority"""
    
    authority_type: str = ""
    """Type of authority"""
    
    @classmethod
    def create(cls, authority_id: str, authority_type: str) -> ContinuityAuthority:
        return cls(authority_id=authority_id, authority_type=authority_type)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "authority_id": self.authority_id,
            "authority_type": self.authority_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContinuityAuthority:
        return cls(
            authority_id=data["authority_id"],
            authority_type=data.get("authority_type", ""),
        )


@dataclass(frozen=True)
class ContinuityOwner:
    """
    Architectural owner of a continuity state.
    
    OWNERSHIP CONTRACT (Part 2):
        CO-OWNER-LAW-001: Continuity ownership is explicit
        CO-OWNER-LAW-002: Ownership never changes implicitly
    """
    
    owner_id: str = ""
    """Identifier of the owner"""
    
    owner_type: str = ""
    """Type of owner (subsystem name)"""
    
    @classmethod
    def create(cls, owner_id: str, owner_type: str) -> ContinuityOwner:
        return cls(owner_id=owner_id, owner_type=owner_type)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "owner_id": self.owner_id,
            "owner_type": self.owner_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContinuityOwner:
        return cls(
            owner_id=data["owner_id"],
            owner_type=data.get("owner_type", ""),
        )


@dataclass(frozen=True)
class ContinuityProjection:
    """
    Semantic projection of continuity state.
    
    OWNERSHIP CONTRACT (Part 2):
        CO-PROJECTION-LAW-001: Projection represents semantic expectation only
    """
    
    projected_state: Dict[str, Any] = field(default_factory=dict)
    """Projected continuity state"""
    
    confidence: float = 1.0
    """Confidence in the projection (semantic, not probabilistic)"""
    
    @classmethod
    def create(
        cls,
        projected_state: Dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> ContinuityProjection:
        return cls(
            projected_state=projected_state or {},
            confidence=confidence,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "projected_state": self.projected_state,
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContinuityProjection:
        return cls(
            projected_state=data.get("projected_state", {}),
            confidence=data.get("confidence", 1.0),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Part 1 - Continuity types
    "ContinuousOrientation",
    "InterruptedOrientation",
    "ResumedOrientation",
    "RestoredOrientation",
    "InheritedOrientation",
    # Part 2 - Contracts
    "ContinuityReference",
    "ContinuityRelationship",
    "ContinuityRequirement",
    "ContinuityAuthority",
    "ContinuityOwner",
    "ContinuityProjection",
]