# Oriented Network Cognitive Load Model - Phase 4.7.8 Part 1 & 2
# ===============================================================

"""
Cognitive Load Model for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Load represents semantic cognitive demand, not runtime profiling
    - No CPU/GPU/memory measurement, no runtime monitoring
    - Pure semantic representation only
    
PHASE 4.7.8 PART 1 - LOAD TYPES:
    OrientationLoad
    ExpectedLoad
    CurrentLoad
    ProjectedLoad
    PeakLoad
    ResidualLoad

PHASE 4.7.8 PART 2 - CONTRACTS:
    LoadReference, LoadRelationship, LoadRequirement,
    LoadAuthority, LoadOwner, LoadProjection
    
NO RUNTIME BEHAVIOR:
    - No profiling execution
    - No runtime monitoring
    - No measurement of CPU/GPU/memory utilization
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from gordon_system.src.agent.components.networks.oriented.persistence.base import (
    BasePersistenceModel,
    PersistenceIdentity,
)


# =============================================================================
# LOAD TYPES (Part 1)
# =============================================================================

@dataclass(frozen=True)
class OrientationLoad(BasePersistenceModel):
    """
    The cognitive load of an orientation.
    
    SEMANTIC ROLE:
        Represents semantic cognitive demand for orientation.
        
    LAWS:
        ORIENTED-LOAD-LAW-001: Load represents semantic cognitive demand
        ORIENTED-LOAD-LAW-002: Load never profiles execution
    """
    
    persistence_type: str = field(default="orientation_load", init=False)
    load_value: float = 1.0
    """Semantic cognitive load value"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        load_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> OrientationLoad:
        return cls(
            persistence_id=persistence_id,
            load_value=load_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "load_value": self.load_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OrientationLoad:
        return cls(
            persistence_id=data["persistence_id"],
            load_value=data.get("load_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.load_value <= 1):
            return False, ("Load value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "load_value": self.load_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ExpectedLoad(BasePersistenceModel):
    """
    The expected cognitive load.
    
    SEMANTIC ROLE:
        Represents semantic expectations about cognitive demand.
        
    LAWS:
        ORIENTED-LOAD-LAW-003: Load never performs runtime monitoring
        ORIENTED-LOAD-LAW-004: Load expresses semantic expectations only
    """
    
    persistence_type: str = field(default="expected_load", init=False)
    expected_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        expected_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> ExpectedLoad:
        return cls(
            persistence_id=persistence_id,
            expected_value=expected_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "expected_value": self.expected_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExpectedLoad:
        return cls(
            persistence_id=data["persistence_id"],
            expected_value=data.get("expected_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.expected_value <= 1):
            return False, ("Expected value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "expected_value": self.expected_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class CurrentLoad(BasePersistenceModel):
    """
    The current cognitive load.
    
    SEMANTIC ROLE:
        Represents semantic expectations about current cognitive demand.
        
    LAWS:
        ORIENTED-LOAD-LAW-005: Load never measures CPU, GPU, or memory utilization
        ORIENTED-LOAD-LAW-006: Load remains immutable
    """
    
    persistence_type: str = field(default="current_load", init=False)
    current_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        current_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> CurrentLoad:
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
    def from_dict(cls, data: Dict[str, Any]) -> CurrentLoad:
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
class ProjectedLoad(BasePersistenceModel):
    """
    The projected cognitive load.
    
    SEMANTIC ROLE:
        Represents semantic projections about future cognitive demand.
        
    LAWS:
        ORIENTED-LOAD-LAW-007: Load remains deterministic
        ORIENTED-LOAD-LAW-008: Load never influences scheduling directly
    """
    
    persistence_type: str = field(default="projected_load", init=False)
    projected_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        projected_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> ProjectedLoad:
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
    def from_dict(cls, data: Dict[str, Any]) -> ProjectedLoad:
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


@dataclass(frozen=True)
class PeakLoad(BasePersistenceModel):
    """
    The peak cognitive load.
    
    SEMANTIC ROLE:
        Represents semantic expectations about maximum cognitive demand.
        
    LAWS:
        ORIENTED-LOAD-LAW-007: Load remains deterministic
        ORIENTED-LOAD-LAW-008: Load never influences scheduling directly
    """
    
    persistence_type: str = field(default="peak_load", init=False)
    peak_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        peak_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> PeakLoad:
        return cls(
            persistence_id=persistence_id,
            peak_value=peak_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "peak_value": self.peak_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PeakLoad:
        return cls(
            persistence_id=data["persistence_id"],
            peak_value=data.get("peak_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.peak_value <= 1):
            return False, ("Peak value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "peak_value": self.peak_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ResidualLoad(BasePersistenceModel):
    """
    The residual cognitive load.
    
    SEMANTIC ROLE:
        Represents semantic expectations about remaining cognitive demand.
        
    LAWS:
        ORIENTED-LOAD-LAW-007: Load remains deterministic
        ORIENTED-LOAD-LAW-008: Load never influences scheduling directly
    """
    
    persistence_type: str = field(default="residual_load", init=False)
    residual_value: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        residual_value: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> ResidualLoad:
        return cls(
            persistence_id=persistence_id,
            residual_value=residual_value,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "residual_value": self.residual_value,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResidualLoad:
        return cls(
            persistence_id=data["persistence_id"],
            residual_value=data.get("residual_value", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.residual_value <= 1):
            return False, ("Residual value must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "residual_value": self.residual_value,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


# =============================================================================
# LOAD CONTRACTS (Part 2)
# =============================================================================

@dataclass(frozen=True)
class LoadReference:
    """
    Reference to a load state.
    
    OWNERSHIP CONTRACT (Part 2):
        LDO-OWNERSHIP-LAW-001: Load owns semantic expectations only
        
    INVARIANTS:
        LR-INV-001: Reference is immutable
        LR-INV-002: Reference never owns the referenced load
        LR-INV-003: Reference maintains identity across revisions
    """
    
    load_id: PersistenceIdentity
    
    revision: int = 1
    
    @classmethod
    def create(cls, load_id: PersistenceIdentity) -> LoadReference:
        return cls(load_id=load_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "load_id": self.load_id,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LoadReference:
        return cls(
            load_id=data["load_id"],
            revision=data.get("revision", 1),
        )


@dataclass(frozen=True)
class LoadProjection:
    """
    Semantic projection of load state.
    
    OWNERSHIP CONTRACT (Part 2):
        LDO-PROJECTION-LAW-001: Projection represents semantic expectation only
    """
    
    projected_state: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    @classmethod
    def create(
        cls,
        projected_state: Dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> LoadProjection:
        return cls(projected_state=projected_state or {}, confidence=confidence)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "projected_state": self.projected_state,
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LoadProjection:
        return cls(
            projected_state=data.get("projected_state", {}),
            confidence=data.get("confidence", 1.0),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Part 1 - Load types
    "OrientationLoad",
    "ExpectedLoad",
    "CurrentLoad",
    "ProjectedLoad",
    "PeakLoad",
    "ResidualLoad",
    # Part 2 - Contracts
    "LoadReference",
    "LoadProjection",
]