# Oriented Network Interruption Model - Phase 4.7.8 Part 1 & 2
# =============================================================

"""
Interruption Model for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Interruption represents semantic interruption, not runtime signal handling
    - Interruption never destroys semantic identity unless explicitly specified
    - Pure semantic representation only
    
PHASE 4.7.8 PART 1 - INTERRUPTION TYPES:
    ExpectedInterruption
    UnexpectedInterruption
    ExternalInterruption
    InternalInterruption
    ExecutiveInterruption
    ResourceInterruption

PHASE 4.7.8 PART 2 - CONTRACTS:
    InterruptionReference, InterruptionRelationship, InterruptionClassification,
    InterruptionAuthority, InterruptionOwner
    
NO RUNTIME BEHAVIOR:
    - No signal handling
    - No runtime interrupts
    - No thread management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from gordon_system.src.agent.components.networks.oriented.persistence.base import (
    BasePersistenceModel,
    PersistenceIdentity,
)


# =============================================================================
# INTERRUPTION CLASSIFICATION TYPES (Part 1)
# =============================================================================

@dataclass(frozen=True)
class ExpectedInterruption(BasePersistenceModel):
    """
    An expected interruption - semantically anticipated.
    
    SEMANTIC ROLE:
        Represents an interruption that was foreseen and accounted for
        in the semantic model. Identity is preserved across such interruption.
        
    LAWS:
        ORIENTED-INTERRUPTION-LAW-001: ExpectedInterruption represents semantic interruption only
        ORIENTED-INTERRUPTION-LAW-002: Interruption does not terminate Orientation
    """
    
    persistence_type: str = field(default="expected_interruption", init=False)
    anticipation_context: str = ""
    """Context that made the interruption expected"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        anticipation_context: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> ExpectedInterruption:
        return cls(
            persistence_id=persistence_id,
            anticipation_context=anticipation_context,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "anticipation_context": self.anticipation_context,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExpectedInterruption:
        return cls(
            persistence_id=data["persistence_id"],
            anticipation_context=data.get("anticipation_context", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "anticipation_context": self.anticipation_context,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class UnexpectedInterruption(BasePersistenceModel):
    """
    An unexpected interruption - semantically unforeseen.
    
    SEMANTIC ROLE:
        Represents an interruption that was not anticipated in the model.
        Semantic identity may be preserved depending on context.
        
    LAWS:
        ORIENTED-INTERRUPTION-LAW-003: UnexpectedInterruption preserves semantic identity
        ORIENTED-INTERRUPTION-LAW-004: Interruption does not terminate Orientation
    """
    
    persistence_type: str = field(default="unexpected_interruption", init=False)
    disruption_reason: str = ""
    """Description of what caused the unexpected interruption"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        disruption_reason: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> UnexpectedInterruption:
        return cls(
            persistence_id=persistence_id,
            disruption_reason=disruption_reason,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "disruption_reason": self.disruption_reason,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UnexpectedInterruption:
        return cls(
            persistence_id=data["persistence_id"],
            disruption_reason=data.get("disruption_reason", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "disruption_reason": self.disruption_reason,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ExternalInterruption(BasePersistenceModel):
    """
    An external interruption - caused by external factors.
    
    SEMANTIC ROLE:
        Represents an interruption originating from outside the system.
        
    LAWS:
        ORIENTED-INTERRUPTION-LAW-005: External interruption preserves identity
        ORIENTED-INTERRUPTION-LAW-006: Identity survives external disruption
    """
    
    persistence_type: str = field(default="external_interruption", init=False)
    source_context: str = ""
    """Source of the external interruption"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        source_context: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> ExternalInterruption:
        return cls(
            persistence_id=persistence_id,
            source_context=source_context,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "source_context": self.source_context,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExternalInterruption:
        return cls(
            persistence_id=data["persistence_id"],
            source_context=data.get("source_context", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "source_context": self.source_context,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class InternalInterruption(BasePersistenceModel):
    """
    An internal interruption - caused by internal factors.
    
    SEMANTIC ROLE:
        Represents an interruption originating from within the system.
        
    LAWS:
        ORIENTED-INTERRUPTION-LAW-007: Internal interruption preserves identity
        ORIENTED-INTERRUPTION-LAW-008: Identity survives internal disruption
    """
    
    persistence_type: str = field(default="internal_interruption", init=False)
    internal_reason: str = ""
    """Internal reason for the interruption"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        internal_reason: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> InternalInterruption:
        return cls(
            persistence_id=persistence_id,
            internal_reason=internal_reason,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "internal_reason": self.internal_reason,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InternalInterruption:
        return cls(
            persistence_id=data["persistence_id"],
            internal_reason=data.get("internal_reason", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "internal_reason": self.internal_reason,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ExecutiveInterruption(BasePersistenceModel):
    """
    An executive interruption - caused by executive decision.
    
    SEMANTIC ROLE:
        Represents an interruption resulting from executive coordination.
        
    LAWS:
        ORIENTED-INTERRUPTION-LAW-009: Executive interruption preserves identity
        ORIENTED-INTERRUPTION-LAW-010: Identity survives executive reorientation
    """
    
    persistence_type: str = field(default="executive_interruption", init=False)
    executive_reason: str = ""
    """Executive decision causing the interruption"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        executive_reason: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> ExecutiveInterruption:
        return cls(
            persistence_id=persistence_id,
            executive_reason=executive_reason,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "executive_reason": self.executive_reason,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveInterruption:
        return cls(
            persistence_id=data["persistence_id"],
            executive_reason=data.get("executive_reason", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "executive_reason": self.executive_reason,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ResourceInterruption(BasePersistenceModel):
    """
    A resource interruption - caused by resource unavailability.
    
    SEMANTIC ROLE:
        Represents an interruption due to unavailable resources.
        
    LAWS:
        ORIENTED-INTERRUPTION-LAW-011: Resource interruption preserves identity
        ORIENTED-INTERRUPTION-LAW-012: Identity survives resource constraints
    """
    
    persistence_type: str = field(default="resource_interruption", init=False)
    resource_context: str = ""
    """Resource constraint causing the interruption"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        resource_context: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> ResourceInterruption:
        return cls(
            persistence_id=persistence_id,
            resource_context=resource_context,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "resource_context": self.resource_context,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResourceInterruption:
        return cls(
            persistence_id=data["persistence_id"],
            resource_context=data.get("resource_context", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "resource_context": self.resource_context,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


# =============================================================================
# INTERRUPTION CONTRACTS (Part 2)
# =============================================================================

@dataclass(frozen=True)
class InterruptionReference:
    """
    Reference to an interruption state.
    
    OWNERSHIP CONTRACT (Part 2):
        INT-OWNERSHIP-LAW-001: Interruption owns semantic representation only
        
    INVARIANTS:
        IR-INV-001: Reference is immutable
        IR-INV-002: Reference never owns the referenced interruption
        IR-INV-003: Reference maintains identity across revisions
    """
    
    interruption_id: PersistenceIdentity
    
    revision: int = 1
    
    @classmethod
    def create(cls, interruption_id: PersistenceIdentity) -> InterruptionReference:
        return cls(interruption_id=interruption_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "interruption_id": self.interruption_id,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InterruptionReference:
        return cls(
            interruption_id=data["interruption_id"],
            revision=data.get("revision", 1),
        )


@dataclass(frozen=True)
class InterruptionRelationship:
    """
    Semantic relationship between interruption states.
    
    OWNERSHIP CONTRACT (Part 2):
        INT-RELATIONSHIP-LAW-001: Relationship represents semantic connection only
    """
    
    source_id: PersistenceIdentity
    target_id: PersistenceIdentity
    relationship_type: str = ""
    
    @classmethod
    def create(
        cls,
        source_id: PersistenceIdentity,
        target_id: PersistenceIdentity,
        relationship_type: str = "",
    ) -> InterruptionRelationship:
        return cls(source_id=source_id, target_id=target_id, relationship_type=relationship_type)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InterruptionRelationship:
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=data.get("relationship_type", ""),
        )


@dataclass(frozen=True)
class InterruptionClassification:
    """
    Classification of interruption semantics.
    
    OWNERSHIP CONTRACT (Part 2):
        INT-CLASSIFICATION-LAW-001: Classification represents semantic category only
    """
    
    classification_type: str = ""
    """Type of interruption classification"""
    
    criteria: str = ""
    """Semantic criteria for the classification"""
    
    @classmethod
    def create(cls, classification_type: str, criteria: str = "") -> InterruptionClassification:
        return cls(classification_type=classification_type, criteria=criteria)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "classification_type": self.classification_type,
            "criteria": self.criteria,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InterruptionClassification:
        return cls(
            classification_type=data["classification_type"],
            criteria=data.get("criteria", ""),
        )


@dataclass(frozen=True)
class InterruptionAuthority:
    """
    Authority specification for interruption.
    
    OWNERSHIP CONTRACT (Part 2):
        INT-AUTHORITY-LAW-001: Authority remains externally defined
    """
    
    authority_id: str = ""
    authority_type: str = ""
    
    @classmethod
    def create(cls, authority_id: str, authority_type: str) -> InterruptionAuthority:
        return cls(authority_id=authority_id, authority_type=authority_type)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "authority_id": self.authority_id,
            "authority_type": self.authority_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InterruptionAuthority:
        return cls(
            authority_id=data["authority_id"],
            authority_type=data.get("authority_type", ""),
        )


@dataclass(frozen=True)
class InterruptionOwner:
    """
    Architectural owner of an interruption state.
    
    OWNERSHIP CONTRACT (Part 2):
        INT-OWNER-LAW-001: Interruption ownership is explicit
        INT-OWNER-LAW-002: Ownership never changes implicitly
    """
    
    owner_id: str = ""
    owner_type: str = ""
    
    @classmethod
    def create(cls, owner_id: str, owner_type: str) -> InterruptionOwner:
        return cls(owner_id=owner_id, owner_type=owner_type)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "owner_id": self.owner_id,
            "owner_type": self.owner_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InterruptionOwner:
        return cls(
            owner_id=data["owner_id"],
            owner_type=data.get("owner_type", ""),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Part 1 - Interruption types
    "ExpectedInterruption",
    "UnexpectedInterruption",
    "ExternalInterruption",
    "InternalInterruption",
    "ExecutiveInterruption",
    "ResourceInterruption",
    # Part 2 - Contracts
    "InterruptionReference",
    "InterruptionRelationship",
    "InterruptionClassification",
    "InterruptionAuthority",
    "InterruptionOwner",
]