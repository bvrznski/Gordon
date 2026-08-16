# Oriented Network Recovery Model - Phase 4.7.8 Part 1 & 2
# ==========================================================

"""
Recovery Model for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Recovery represents semantic restoration, not runtime execution restart
    - Recovery preserves semantic identity when possible
    - Pure semantic representation only
    
PHASE 4.7.8 PART 1 - RECOVERY TYPES:
    RecoveryCandidate
    RecoveredOrientation
    RecoveryContext
    RecoveryRequirement
    RecoveryRelationship

PHASE 4.7.8 PART 2 - CONTRACTS:
    RecoveryReference, RecoveryRelationship, RecoveryRequirement,
    RecoveryAuthority, RecoveryOwner, RecoveryProjection
    
NO RUNTIME BEHAVIOR:
    - No restart logic
    - No execution restoration
    - No checkpoint loading
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from gordon_system.src.agent.components.networks.oriented.persistence.base import (
    BasePersistenceModel,
    PersistenceIdentity,
)


# =============================================================================
# RECOVERY TYPES (Part 1)
# =============================================================================

@dataclass(frozen=True)
class RecoveryCandidate(BasePersistenceModel):
    """
    A candidate for recovery.
    
    SEMANTIC ROLE:
        Represents an orientation state that could potentially be recovered.
        
    LAWS:
        ORIENTED-RECOVERY-LAW-001: RecoveryCandidate represents potential recovery
        ORIENTED-RECOVERY-LAW-002: Recovery preserves semantic identity whenever possible
    """
    
    persistence_type: str = field(default="recovery_candidate", init=False)
    candidate_source: PersistenceIdentity = ""
    """Source that could be recovered"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        candidate_source: PersistenceIdentity = "",
        revision: int = 1,
        version: int = 1,
    ) -> RecoveryCandidate:
        return cls(
            persistence_id=persistence_id,
            candidate_source=candidate_source,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "candidate_source": self.candidate_source,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveryCandidate:
        return cls(
            persistence_id=data["persistence_id"],
            candidate_source=data.get("candidate_source", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "candidate_source": self.candidate_source,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        if self.candidate_source:
            return (self.candidate_source,)
        return ()


@dataclass(frozen=True)
class RecoveredOrientation(BasePersistenceModel):
    """
    An orientation that has been recovered.
    
    SEMANTIC ROLE:
        Represents an orientation state after successful recovery.
        
    LAWS:
        ORIENTED-RECOVERY-LAW-003: RecoveredOrientation preserves semantic identity
        ORIENTED-RECOVERY-LAW-004: Recovery preserves continuity when possible
    """
    
    persistence_type: str = field(default="recovered_orientation", init=False)
    recovery_source: PersistenceIdentity = ""
    """Source from which orientation was recovered"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        recovery_source: PersistenceIdentity = "",
        revision: int = 1,
        version: int = 1,
    ) -> RecoveredOrientation:
        return cls(
            persistence_id=persistence_id,
            recovery_source=recovery_source,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "recovery_source": self.recovery_source,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveredOrientation:
        return cls(
            persistence_id=data["persistence_id"],
            recovery_source=data.get("recovery_source", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "recovery_source": self.recovery_source,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        if self.recovery_source:
            return (self.recovery_source,)
        return ()


@dataclass(frozen=True)
class RecoveryContext(BasePersistenceModel):
    """
    Context information for a recovery operation.
    
    SEMANTIC ROLE:
        Represents the semantic context during recovery.
        
    LAWS:
        ORIENTED-RECOVERY-LAW-005: RecoveryContext represents recovery state
        ORIENTED-RECOVERY-LAW-006: Recovery preserves lineage
    """
    
    persistence_type: str = field(default="recovery_context", init=False)
    context_state: Dict[str, Any] = field(default_factory=dict)
    """Context state during recovery"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        context_state: Dict[str, Any] | None = None,
        revision: int = 1,
        version: int = 1,
    ) -> RecoveryContext:
        return cls(
            persistence_id=persistence_id,
            context_state=context_state or {},
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "context_state": self.context_state,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveryContext:
        return cls(
            persistence_id=data["persistence_id"],
            context_state=data.get("context_state", {}),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "context_state": self.context_state,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class RecoveryRequirement(BasePersistenceModel):
    """
    Semantic requirement for recovery.
    
    SEMANTIC ROLE:
        Represents the conditions that must be satisfied for successful recovery.
        
    LAWS:
        ORIENTED-RECOVERY-LAW-007: RecoveryRequirement describes semantic expectations
        ORIENTED-RECOVERY-LAW-008: Requirements remain immutable
    """
    
    persistence_type: str = field(default="recovery_requirement", init=False)
    requirement_type: str = ""
    """Type of recovery requirement"""
    
    condition: str = ""
    """Semantic condition for recovery"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        requirement_type: str = "",
        condition: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> RecoveryRequirement:
        return cls(
            persistence_id=persistence_id,
            requirement_type=requirement_type,
            condition=condition,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "requirement_type": self.requirement_type,
            "condition": self.condition,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveryRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            requirement_type=data.get("requirement_type", ""),
            condition=data.get("condition", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "requirement_type": self.requirement_type,
            "condition": self.condition,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class RecoveryRelationship(BasePersistenceModel):
    """
    Semantic relationship in recovery.
    
    SEMANTIC ROLE:
        Represents semantic connections during recovery operations.
        
    LAWS:
        ORIENTED-RECOVERY-LAW-009: RecoveryRelationship represents semantic connection
        ORIENTED-RECOVERY-LAW-010: Relationships remain typed and explicit
    """
    
    persistence_type: str = field(default="recovery_relationship", init=False)
    source_id: PersistenceIdentity = ""
    """Source of the relationship"""
    
    target_id: PersistenceIdentity = ""
    """Target of the relationship"""
    
    relationship_type: str = ""
    """Type of recovery relationship"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        source_id: PersistenceIdentity = "",
        target_id: PersistenceIdentity = "",
        relationship_type: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> RecoveryRelationship:
        return cls(
            persistence_id=persistence_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveryRelationship:
        return cls(
            persistence_id=data["persistence_id"],
            source_id=data.get("source_id", ""),
            target_id=data.get("target_id", ""),
            relationship_type=data.get("relationship_type", ""),
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
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        result = []
        if self.source_id:
            result.append(self.source_id)
        if self.target_id:
            result.append(self.target_id)
        return tuple(result)


# =============================================================================
# RECOVERY CONTRACTS (Part 2)
# =============================================================================

@dataclass(frozen=True)
class RecoveryReference:
    """
    Reference to a recovery state.
    
    OWNERSHIP CONTRACT (Part 2):
        REC-OWNERSHIP-LAW-001: Recovery owns semantic representation only
        
    INVARIANTS:
        RR-INV-001: Reference is immutable
        RR-INV-002: Reference never owns the referenced recovery
        RR-INV-003: Reference maintains identity across revisions
    """
    
    recovery_id: PersistenceIdentity
    
    revision: int = 1
    
    @classmethod
    def create(cls, recovery_id: PersistenceIdentity) -> RecoveryReference:
        return cls(recovery_id=recovery_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recovery_id": self.recovery_id,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveryReference:
        return cls(
            recovery_id=data["recovery_id"],
            revision=data.get("revision", 1),
        )


@dataclass(frozen=True)
class RecoveryProjection:
    """
    Semantic projection of recovery state.
    
    OWNERSHIP CONTRACT (Part 2):
        REC-PROJECTION-LAW-001: Projection represents semantic expectation only
    """
    
    projected_state: Dict[str, Any] = field(default_factory=dict)
    """Projected recovery state"""
    
    confidence: float = 1.0
    
    @classmethod
    def create(
        cls,
        projected_state: Dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> RecoveryProjection:
        return cls(projected_state=projected_state or {}, confidence=confidence)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "projected_state": self.projected_state,
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveryProjection:
        return cls(
            projected_state=data.get("projected_state", {}),
            confidence=data.get("confidence", 1.0),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Part 1 - Recovery types
    "RecoveryCandidate",
    "RecoveredOrientation",
    "RecoveryContext",
    "RecoveryRequirement",
    "RecoveryRelationship",
    # Part 2 - Contracts
    "RecoveryReference",
    "RecoveryProjection",
]