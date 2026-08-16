# Oriented Network Capacity Model - Phase 4.7.8 Part 1 & 2
# ==========================================================

"""
Capacity Model for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Capacity represents semantic expectations, not resource allocation
    - No memory allocation, no scheduling, no runtime measurement
    - Pure semantic representation only
    
PHASE 4.7.8 PART 1 - CAPACITY TYPES:
    OrientationCapacity
    CurrentCapacity
    RequiredCapacity
    AvailableCapacity
    ProjectedCapacity

PHASE 4.7.8 PART 2 - CONTRACTS:
    CapacityReference, CapacityRelationship, CapacityRequirement,
    CapacityAuthority, CapacityOwner, CapacityProjection
    
NO RUNTIME BEHAVIOR:
    - No resource allocation
    - No memory allocation
    - No scheduling
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from gordon_system.src.agent.components.networks.oriented.persistence.base import (
    BasePersistenceModel,
    PersistenceIdentity,
)


# =============================================================================
# CAPACITY TYPES (Part 1)
# =============================================================================

@dataclass(frozen=True)
class OrientationCapacity(BasePersistenceModel):
    """
    The capacity of an orientation.
    
    SEMANTIC ROLE:
        Represents semantic expectations about orientation capacity.
        
    LAWS:
        ORIENTED-CAPACITY-LAW-001: Capacity represents semantic expectations
        ORIENTED-CAPACITY-LAW-002: Capacity never allocates resources
    """
    
    persistence_type: str = field(default="orientation_capacity", init=False)
    capacity_value: float = 1.0
    """Semantic capacity value"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        capacity_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> OrientationCapacity:
        return cls(
            persistence_id=persistence_id,
            capacity_value=capacity_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "capacity_value": self.capacity_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OrientationCapacity:
        return cls(
            persistence_id=data["persistence_id"],
            capacity_value=data.get("capacity_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.capacity_value <= 1):
            return False, ("Capacity value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "capacity_value": self.capacity_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class CurrentCapacity(BasePersistenceModel):
    """
    The current capacity state.
    
    SEMANTIC ROLE:
        Represents the current semantic capacity expectation.
        
    LAWS:
        ORIENTED-CAPACITY-LAW-003: Capacity may express future cognitive requirements
        ORIENTED-CAPACITY-LAW-004: Capacity remains independent from scheduler implementation
    """
    
    persistence_type: str = field(default="current_capacity", init=False)
    current_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        current_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> CurrentCapacity:
        return cls(
            persistence_id=persistence_id,
            current_value=current_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "current_value": self.current_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CurrentCapacity:
        return cls(
            persistence_id=data["persistence_id"],
            current_value=data.get("current_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.current_value <= 1):
            return False, ("Current value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "current_value": self.current_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class RequiredCapacity(BasePersistenceModel):
    """
    The required capacity for a task or goal.
    
    SEMANTIC ROLE:
        Represents semantic expectations about required capacity.
        
    LAWS:
        ORIENTED-CAPACITY-LAW-005: Capacity remains independent from Working Memory implementation
        ORIENTED-CAPACITY-LAW-006: Capacity remains immutable
    """
    
    persistence_type: str = field(default="required_capacity", init=False)
    required_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        required_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> RequiredCapacity:
        return cls(
            persistence_id=persistence_id,
            required_value=required_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "required_value": self.required_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RequiredCapacity:
        return cls(
            persistence_id=data["persistence_id"],
            required_value=data.get("required_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.required_value <= 1):
            return False, ("Required value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "required_value": self.required_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class AvailableCapacity(BasePersistenceModel):
    """
    The available capacity.
    
    SEMANTIC ROLE:
        Represents semantic expectations about available capacity.
        
    LAWS:
        ORIENTED-CAPACITY-LAW-007: Capacity remains immutable
        ORIENTED-CAPACITY-LAW-008: Capacity remains deterministic
    """
    
    persistence_type: str = field(default="available_capacity", init=False)
    available_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        available_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> AvailableCapacity:
        return cls(
            persistence_id=persistence_id,
            available_value=available_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "available_value": self.available_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AvailableCapacity:
        return cls(
            persistence_id=data["persistence_id"],
            available_value=data.get("available_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.available_value <= 1):
            return False, ("Available value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "available_value": self.available_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ProjectedCapacity(BasePersistenceModel):
    """
    The projected capacity.
    
    SEMANTIC ROLE:
        Represents semantic projections about future capacity needs.
        
    LAWS:
        ORIENTED-CAPACITY-LAW-005: Capacity may express future cognitive requirements
        ORIENTED-CAPACITY-LAW-007: Capacity remains immutable
    """
    
    persistence_type: str = field(default="projected_capacity", init=False)
    projected_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        projected_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> ProjectedCapacity:
        return cls(
            persistence_id=persistence_id,
            projected_value=projected_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "projected_value": self.projected_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectedCapacity:
        return cls(
            persistence_id=data["persistence_id"],
            projected_value=data.get("projected_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.projected_value <= 1):
            return False, ("Projected value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "projected_value": self.projected_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


# =============================================================================
# CAPACITY CONTRACTS (Part 2)
# =============================================================================

@dataclass(frozen=True)
class CapacityReference:
    """
    Reference to a capacity state.
    
    OWNERSHIP CONTRACT (Part 2):
        CAP-OWNERSHIP-LAW-001: Capacity owns semantic expectations only
        
    INVARIANTS:
        CR-INV-001: Reference is immutable
        CR-INV-002: Reference never owns the referenced capacity
        CR-INV-003: Reference maintains identity across revisions
    """
    
    capacity_id: PersistenceIdentity
    
    revision: int = 1
    
    @classmethod
    def create(cls, capacity_id: PersistenceIdentity) -> CapacityReference:
        return cls(capacity_id=capacity_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "capacity_id": self.capacity_id,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CapacityReference:
        return cls(
            capacity_id=data["capacity_id"],
            revision=data.get("revision", 1),
        )


@dataclass(frozen=True)
class CapacityProjection:
    """
    Semantic projection of capacity state.
    
    OWNERSHIP CONTRACT (Part 2):
        CAP-PROJECTION-LAW-001: Projection represents semantic expectation only
    """
    
    projected_state: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    @classmethod
    def create(
        cls,
        projected_state: Dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> CapacityProjection:
        return cls(projected_state=projected_state or {}, confidence=confidence)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "projected_state": self.projected_state,
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CapacityProjection:
        return cls(
            projected_state=data.get("projected_state", {}),
            confidence=data.get("confidence", 1.0),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Part 1 - Capacity types
    "OrientationCapacity",
    "CurrentCapacity",
    "RequiredCapacity",
    "AvailableCapacity",
    "ProjectedCapacity",
    # Part 2 - Contracts
    "CapacityReference",
    "CapacityProjection",
]