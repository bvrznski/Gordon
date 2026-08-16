# Oriented Network Requirement Model - Phase 4.7.8 Part 1 & 2
# ============================================================

"""
Requirement Model for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Requirements describe semantic expectations, not resource allocation
    - No implementations, no resources, no schedulers
    - Pure semantic representation only
    
PHASE 4.7.8 PART 1 - REQUIREMENT TYPES:
    AttentionRequirement
    WorkspaceRequirement
    WorkingMemoryRequirement
    ExecutiveRequirement
    ReasoningRequirement
    PlanningRequirement
    MotivationRequirement
    SalienceRequirement

PHASE 4.7.8 PART 2 - CONTRACTS:
    RequirementReference, RequirementRelationship,
    RequirementAuthority, RequirementOwner, RequirementProjection
    
NO RUNTIME BEHAVIOR:
    - No resource allocation
    - No scheduler implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from gordon_system.src.agent.components.networks.oriented.persistence.base import (
    BasePersistenceModel,
    PersistenceIdentity,
)


# =============================================================================
# REQUIREMENT TYPES (Part 1)
# =============================================================================

@dataclass(frozen=True)
class Requirement(BasePersistenceModel):
    """
    A semantic requirement.
    
    SEMANTIC ROLE:
        Represents a semantic expectation that must be satisfied.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-001: Requirements describe semantic expectations
        ORIENTED-REQUIREMENT-LAW-002: Requirements never allocate resources
    """
    
    persistence_type: str = field(default="requirement", init=False)
    requirement_type: str = ""
    """Type of requirement"""
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        requirement_type: str = "",
        revision: int = 1,
        version: int = 1,
    ) -> Requirement:
        return cls(
            persistence_id=persistence_id,
            requirement_type=requirement_type,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "requirement_type": self.requirement_type,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Requirement:
        return cls(
            persistence_id=data["persistence_id"],
            requirement_type=data.get("requirement_type", ""),
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
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class AttentionRequirement(BasePersistenceModel):
    """
    A requirement for attention resources.
    
    SEMANTIC ROLE:
        Represents semantic expectations about attention requirements.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-003: Requirements never schedule execution
        ORIENTED-REQUIREMENT-LAW-004: Requirements remain immutable
    """
    
    persistence_type: str = field(default="attention_requirement", init=False)
    attention_level: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        attention_level: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> AttentionRequirement:
        return cls(
            persistence_id=persistence_id,
            attention_level=attention_level,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "attention_level": self.attention_level,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AttentionRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            attention_level=data.get("attention_level", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.attention_level <= 1):
            return False, ("Attention level must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "attention_level": self.attention_level,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class WorkspaceRequirement(BasePersistenceModel):
    """
    A requirement for workspace resources.
    
    SEMANTIC ROLE:
        Represents semantic expectations about workspace requirements.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-004: Requirements remain immutable
        ORIENTED-REQUIREMENT-LAW-005: Requirements remain repository-independent
    """
    
    persistence_type: str = field(default="workspace_requirement", init=False)
    workspace_size: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        workspace_size: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> WorkspaceRequirement:
        return cls(
            persistence_id=persistence_id,
            workspace_size=workspace_size,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "workspace_size": self.workspace_size,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkspaceRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            workspace_size=data.get("workspace_size", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.workspace_size <= 1):
            return False, ("Workspace size must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "workspace_size": self.workspace_size,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class WorkingMemoryRequirement(BasePersistenceModel):
    """
    A requirement for working memory.
    
    SEMANTIC ROLE:
        Represents semantic expectations about working memory requirements.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-004: Requirements remain immutable
        ORIENTED-REQUIREMENT-LAW-005: Requirements remain repository-independent
    """
    
    persistence_type: str = field(default="working_memory_requirement", init=False)
    memory_capacity: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        memory_capacity: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> WorkingMemoryRequirement:
        return cls(
            persistence_id=persistence_id,
            memory_capacity=memory_capacity,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "memory_capacity": self.memory_capacity,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkingMemoryRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            memory_capacity=data.get("memory_capacity", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.memory_capacity <= 1):
            return False, ("Memory capacity must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "memory_capacity": self.memory_capacity,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ExecutiveRequirement(BasePersistenceModel):
    """
    A requirement for executive resources.
    
    SEMANTIC ROLE:
        Represents semantic expectations about executive requirements.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-004: Requirements remain immutable
        ORIENTED-REQUIREMENT-LAW-005: Requirements remain repository-independent
    """
    
    persistence_type: str = field(default="executive_requirement", init=False)
    executive_load: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        executive_load: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> ExecutiveRequirement:
        return cls(
            persistence_id=persistence_id,
            executive_load=executive_load,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "executive_load": self.executive_load,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            executive_load=data.get("executive_load", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.executive_load <= 1):
            return False, ("Executive load must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "executive_load": self.executive_load,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class ReasoningRequirement(BasePersistenceModel):
    """
    A requirement for reasoning resources.
    
    SEMANTIC ROLE:
        Represents semantic expectations about reasoning requirements.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-004: Requirements remain immutable
        ORIENTED-REQUIREMENT-LAW-005: Requirements remain repository-independent
    """
    
    persistence_type: str = field(default="reasoning_requirement", init=False)
    reasoning_load: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        reasoning_load: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> ReasoningRequirement:
        return cls(
            persistence_id=persistence_id,
            reasoning_load=reasoning_load,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "reasoning_load": self.reasoning_load,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReasoningRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            reasoning_load=data.get("reasoning_load", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.reasoning_load <= 1):
            return False, ("Reasoning load must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "reasoning_load": self.reasoning_load,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class PlanningRequirement(BasePersistenceModel):
    """
    A requirement for planning resources.
    
    SEMANTIC ROLE:
        Represents semantic expectations about planning requirements.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-004: Requirements remain immutable
        ORIENTED-REQUIREMENT-LAW-005: Requirements remain repository-independent
    """
    
    persistence_type: str = field(default="planning_requirement", init=False)
    planning_load: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        planning_load: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> PlanningRequirement:
        return cls(
            persistence_id=persistence_id,
            planning_load=planning_load,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "planning_load": self.planning_load,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlanningRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            planning_load=data.get("planning_load", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.planning_load <= 1):
            return False, ("Planning load must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "planning_load": self.planning_load,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class MotivationRequirement(BasePersistenceModel):
    """
    A requirement for motivation resources.
    
    SEMANTIC ROLE:
        Represents semantic expectations about motivation requirements.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-004: Requirements remain immutable
        ORIENTED-REQUIREMENT-LAW-005: Requirements remain repository-independent
    """
    
    persistence_type: str = field(default="motivation_requirement", init=False)
    motivation_level: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        motivation_level: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> MotivationRequirement:
        return cls(
            persistence_id=persistence_id,
            motivation_level=motivation_level,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "motivation_level": self.motivation_level,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MotivationRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            motivation_level=data.get("motivation_level", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.motivation_level <= 1):
            return False, ("Motivation level must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "motivation_level": self.motivation_level,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


@dataclass(frozen=True)
class SalienceRequirement(BasePersistenceModel):
    """
    A requirement for salience resources.
    
    SEMANTIC ROLE:
        Represents semantic expectations about salience requirements.
        
    LAWS:
        ORIENTED-REQUIREMENT-LAW-004: Requirements remain immutable
        ORIENTED-REQUIREMENT-LAW-005: Requirements remain repository-independent
    """
    
    persistence_type: str = field(default="salience_requirement", init=False)
    salience_level: float = 1.0
    
    @classmethod
    def create(
        cls,
        persistence_id: PersistenceIdentity,
        salience_level: float = 1.0,
        revision: int = 1,
        version: int = 1,
    ) -> SalienceRequirement:
        return cls(
            persistence_id=persistence_id,
            salience_level=salience_level,
            revision=revision,
            version=version,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persistence_id": self.persistence_id,
            "salience_level": self.salience_level,
            "revision": self.revision,
            "version": self.version,
            "persistence_type": self.persistence_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SalienceRequirement:
        return cls(
            persistence_id=data["persistence_id"],
            salience_level=data.get("salience_level", 1.0),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        if not self.persistence_id:
            return False, ("Persistence ID is required",)
        if not (0 <= self.salience_level <= 1):
            return False, ("Salience level must be between 0 and 1",)
        return True, ()
    
    def get_provenance(self) -> Dict[str, Any]:
        return {
            "salience_level": self.salience_level,
        }
    
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        return ()


# =============================================================================
# REQUIREMENT CONTRACTS (Part 2)
# =============================================================================

@dataclass(frozen=True)
class RequirementReference:
    """
    Reference to a requirement state.
    
    OWNERSHIP CONTRACT (Part 2):
        REQ-OWNERSHIP-LAW-001: Requirements own semantic expectations only
        
    INVARIANTS:
        RR-INV-001: Reference is immutable
        RR-INV-002: Reference never owns the referenced requirement
        RR-INV-003: Reference maintains identity across revisions
    """
    
    requirement_id: PersistenceIdentity
    
    revision: int = 1
    
    @classmethod
    def create(cls, requirement_id: PersistenceIdentity) -> RequirementReference:
        return cls(requirement_id=requirement_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RequirementReference:
        return cls(
            requirement_id=data["requirement_id"],
            revision=data.get("revision", 1),
        )


@dataclass(frozen=True)
class RequirementProjection:
    """
    Semantic projection of requirement state.
    
    OWNERSHIP CONTRACT (Part 2):
        REQ-PROJECTION-LAW-001: Projection represents semantic expectation only
    """
    
    projected_state: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    @classmethod
    def create(
        cls,
        projected_state: Dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> RequirementProjection:
        return cls(projected_state=projected_state or {}, confidence=confidence)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "projected_state": self.projected_state,
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RequirementProjection:
        return cls(
            projected_state=data.get("projected_state", {}),
            confidence=data.get("confidence", 1.0),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Part 1 - Requirement types
    "Requirement",
    "AttentionRequirement",
    "WorkspaceRequirement",
    "WorkingMemoryRequirement",
    "ExecutiveRequirement",
    "ReasoningRequirement",
    "PlanningRequirement",
    "MotivationRequirement",
    "SalienceRequirement",
    # Part 2 - Contracts
    "RequirementReference",
    "RequirementProjection",
]