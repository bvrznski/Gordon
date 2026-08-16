# Oriented Network Working Memory Integration Contracts
# ======================================================

"""
Working Memory integration contracts for Phase 4.7.7.

OWNERSHIP:
    - Working Memory owns: active cognitive maintenance, transient representations,
      active recall, active manipulation
    - Oriented Network references: working memory state, projections, requirements

SEMANTIC INTEGRATION PRINCIPLES:
    - Never manage or own working memory
    - Consume working memory projections only
    - Express requirements, never implement them

INTEGRATION LAWS:
    ORIENTED-COGNITIVE-INTEGRATION-LAW-006: Working Memory remains sole owner
    ORIENTED-COGNITIVE-INTEGRATION-LAW-019: Integration shall never manage Working Memory
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


# =============================================================================
# WORKING MEMORY REFERENCES - Semantic references to working memory concepts
# =============================================================================


@dataclass(frozen=True)
class WorkingMemoryReference:
    """
    Reference to a working memory concept without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every reference shall be explicit
        INTEGRATION-LAW-014: Every dependency shall be explicit
    """
    
    working_memory_id: str = field(default="unnamed")
    """Unique identifier for the working memory concept being referenced"""
    
    reference_type: str = field(default="context")
    """Type of working memory reference (context, projection, requirement)"""
    
    priority_level: Optional[str] = None
    """Priority level hint (low, medium, high, critical - semantic only)"""
    
    retention_hint_seconds: Optional[float] = None
    """Optional retention duration hint in seconds"""
    
    @classmethod
    def context(cls, working_memory_id: str) -> "WorkingMemoryReference":
        """
        Create a reference to working memory context.
        
        Args:
            working_memory_id: ID of the working memory context
            
        Returns:
            New WorkingMemoryReference instance
        """
        return cls(working_memory_id=working_memory_id, reference_type="context")
    
    @classmethod
    def projection(cls, working_memory_id: str) -> "WorkingMemoryReference":
        """
        Create a reference to a working memory projection.
        
        Args:
            working_memory_id: ID of the working memory projection
            
        Returns:
            New WorkingMemoryReference instance
        """
        return cls(working_memory_id=working_memory_id, reference_type="projection")
    
    @classmethod
    def requirement(cls, working_memory_id: str) -> "WorkingMemoryReference":
        """
        Create a reference to a working memory requirement.
        
        Args:
            working_memory_id: ID of the working memory requirement
            
        Returns:
            New WorkingMemoryReference instance
        """
        return cls(working_memory_id=working_memory_id, reference_type="requirement")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "working_memory_id": self.working_memory_id,
            "reference_type": self.reference_type,
            "priority_level": self.priority_level,
            "retention_hint_seconds": self.retention_hint_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemoryReference":
        """Deserialize from dictionary."""
        return cls(
            working_memory_id=data.get("working_memory_id", "unnamed"),
            reference_type=data.get("reference_type", "context"),
            priority_level=data.get("priority_level"),
            retention_hint_seconds=data.get("retention_hint_seconds"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the reference."""
        errors = []
        if not self.working_memory_id:
            errors.append("working_memory_id must be non-empty")
        if self.reference_type not in ("context", "projection", "requirement"):
            errors.append(f"invalid reference_type: {self.reference_type}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkingMemoryReference:\n{error_str}")


# =============================================================================
# WORKING MEMORY CONTEXT - Immutable working memory state projection
# =============================================================================


@dataclass(frozen=True)
class WorkingMemoryContext:
    """
    Projection of current working memory state without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-019: Integration shall never manage Working Memory
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
    """
    
    context_id: str = field(default="unnamed")
    """Unique identifier for this working memory context"""
    
    active_items: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently active items in working memory"""
    
    item_priority_map: Dict[str, float] = field(default_factory=dict)
    """Priority levels per item (semantic only)"""
    
    total_item_count: int = 0
    """Total number of items in working memory"""
    
    estimated_stable_seconds: Optional[float] = None
    """Estimated duration of current working memory state"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemoryContext":
        """Deserialize from dictionary."""
        active = tuple(data.get("active_items", []))
        priority = dict(data.get("item_priority_map", {}))
        
        return cls(
            context_id=data.get("context_id", "unnamed"),
            active_items=active,
            item_priority_map=priority,
            total_item_count=int(data.get("total_item_count", 0)),
            estimated_stable_seconds=data.get("estimated_stable_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "context_id": self.context_id,
            "active_items": list(self.active_items),
            "item_priority_map": dict(self.item_priority_map),
            "total_item_count": self.total_item_count,
            "estimated_stable_seconds": self.estimated_stable_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the context."""
        errors = []
        if not self.context_id:
            errors.append("context_id must be non-empty")
        for value in self.item_priority_map.values():
            if not (0.0 <= value <= 1.0):
                errors.append(f"invalid priority value: {value}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkingMemoryContext:\n{error_str}")


# =============================================================================
# WORKING MEMORY PROJECTION - Information about working memory state
# =============================================================================


@dataclass(frozen=True)
class WorkingMemoryProjection:
    """
    Projection of working memory information without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-019: Integration shall never manage Working Memory
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    projection_id: str = field(default="unnamed")
    """Unique identifier for this projection"""
    
    context: WorkingMemoryContext = field(default_factory=WorkingMemoryContext)
    """Current working memory context"""
    
    available_working_memory_capacity: float = field(default=1.0)
    """Available working memory capacity as ratio (0.0 to 1.0)"""
    
    estimated_stable_seconds: Optional[float] = None
    """Estimated duration of current working memory state"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemoryProjection":
        """Deserialize from dictionary."""
        context_data = data.get("context", {})
        if isinstance(context_data, dict):
            context = WorkingMemoryContext.from_dict(context_data)
        else:
            context = WorkingMemoryContext()
        
        return cls(
            projection_id=data.get("projection_id", "unnamed"),
            context=context,
            available_working_memory_capacity=float(data.get("available_working_memory_capacity", 1.0)),
            estimated_stable_seconds=data.get("estimated_stable_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "projection_id": self.projection_id,
            "context": self.context.to_dict(),
            "available_working_memory_capacity": self.available_working_memory_capacity,
            "estimated_stable_seconds": self.estimated_stable_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the projection."""
        errors = []
        if not self.projection_id:
            errors.append("projection_id must be non-empty")
        if not (0.0 <= self.available_working_memory_capacity <= 1.0):
            errors.append(f"invalid capacity value: {self.available_working_memory_capacity}")
        
        context_valid, context_errors = self.context.validate()
        if not context_valid:
            errors.extend(context_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkingMemoryProjection:\n{error_str}")


# =============================================================================
# WORKING MEMORY RELATIONSHIP - Semantic relationship to working memory
# =============================================================================


@dataclass(frozen=True)
class WorkingMemoryRelationship:
    """
    Semantic relationship between orientation and working memory.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every relationship shall be explicit
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    relationship_id: str = field(default="unnamed")
    """Unique identifier for this relationship"""
    
    working_memory_reference: WorkingMemoryReference = field(
        default_factory=lambda: WorkingMemoryReference()
    )
    """Reference to the working memory being related to"""
    
    relationship_type: str = field(default="consume")
    """Type of relationship (consume, reference, require)"""
    
    purpose: str = field(default="")
    """Semantic purpose of this relationship"""
    
    @classmethod
    def consume(
        cls, working_memory_id: str, purpose: str = ""
    ) -> "WorkingMemoryRelationship":
        """
        Create a consumption relationship.
        
        Args:
            working_memory_id: ID of the working memory to consume
            purpose: Semantic purpose
            
        Returns:
            New WorkingMemoryRelationship instance
        """
        return cls(
            relationship_id=f"consume_{working_memory_id}",
            working_memory_reference=WorkingMemoryReference(working_memory_id, "context"),
            relationship_type="consume",
            purpose=purpose,
        )
    
    @classmethod
    def reference(
        cls, working_memory_id: str, purpose: str = ""
    ) -> "WorkingMemoryRelationship":
        """
        Create a reference relationship.
        
        Args:
            working_memory_id: ID of the working memory to reference
            purpose: Semantic purpose
            
        Returns:
            New WorkingMemoryRelationship instance
        """
        return cls(
            relationship_id=f"reference_{working_memory_id}",
            working_memory_reference=WorkingMemoryReference(working_memory_id, "projection"),
            relationship_type="reference",
            purpose=purpose,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "relationship_id": self.relationship_id,
            "working_memory_reference": self.working_memory_reference.to_dict(),
            "relationship_type": self.relationship_type,
            "purpose": self.purpose,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemoryRelationship":
        """Deserialize from dictionary."""
        ref_data = data.get("working_memory_reference", {})
        if isinstance(ref_data, dict):
            working_memory_ref = WorkingMemoryReference.from_dict(ref_data)
        else:
            working_memory_ref = WorkingMemoryReference()
        
        return cls(
            relationship_id=data.get("relationship_id", "unnamed"),
            working_memory_reference=working_memory_ref,
            relationship_type=data.get("relationship_type", "consume"),
            purpose=data.get("purpose", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the relationship."""
        errors = []
        if not self.relationship_id:
            errors.append("relationship_id must be non-empty")
        if self.relationship_type not in ("consume", "reference", "require"):
            errors.append(f"invalid relationship_type: {self.relationship_type}")
        
        ref_valid, ref_errors = self.working_memory_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkingMemoryRelationship:\n{error_str}")


# =============================================================================
# WORKING MEMORY INFLUENCE - Semantic influence on working memory
# =============================================================================


@dataclass(frozen=True)
class WorkingMemoryInfluence:
    """
    Semantic influence that orientation may have on working memory.
    
    DESCRIBES what influence the Oriented Network can express without owning
    or implementing it. This is NOT a directive, only a semantic expectation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-019: Integration shall never manage Working Memory
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    influence_id: str = field(default="unnamed")
    """Unique identifier for this influence"""
    
    influence_type: str = field(default="requirement")
    """Type of influence (requirement, expectation, suggestion)"""
    
    target_working_memory: Optional[str] = None
    """Target working memory ID if applicable"""
    
    expected_state: Dict[str, Any] = field(default_factory=dict)
    """Expected state description (semantic only)"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemoryInfluence":
        """Deserialize from dictionary."""
        return cls(
            influence_id=data.get("influence_id", "unnamed"),
            influence_type=data.get("influence_type", "requirement"),
            target_working_memory=data.get("target_working_memory"),
            expected_state=dict(data.get("expected_state", {})),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "influence_id": self.influence_id,
            "influence_type": self.influence_type,
            "target_working_memory": self.target_working_memory,
            "expected_state": dict(self.expected_state),
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the influence."""
        errors = []
        if not self.influence_id:
            errors.append("influence_id must be non-empty")
        if self.influence_type not in ("requirement", "expectation", "suggestion"):
            errors.append(f"invalid influence_type: {self.influence_type}")
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkingMemoryInfluence:\n{error_str}")


# =============================================================================
# WORKING MEMORY INTEGRATION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class WorkingMemoryIntegrationContract:
    """
    Complete integration contract for Working Memory.
    
    Combines all semantic elements needed for orientation to interact with
    the working memory system without ownership or implementation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-006: Working Memory remains sole owner
        INTEGRATION-LAW-019: Integration shall never manage Working Memory
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
        INTEGRATION-LAW-027: Deterministic serialization support
    """
    
    contract_id: str = field(default="unnamed")
    """Unique identifier for this integration contract"""
    
    revision: int = field(default=1)
    """Semantic revision number"""
    
    working_memory_reference: WorkingMemoryReference = field(
        default_factory=lambda: WorkingMemoryReference()
    )
    """Primary working memory reference"""
    
    working_memory_context: Optional[WorkingMemoryContext] = None
    """Current working memory context (if available)"""
    
    working_memory_projection: Optional[WorkingMemoryProjection] = None
    """Working memory projection (if available)"""
    
    relationships: Tuple[WorkingMemoryRelationship, ...] = field(default_factory=tuple)
    """Semantic relationships to working memory"""
    
    influences: Tuple[WorkingMemoryInfluence, ...] = field(default_factory=tuple)
    """Semantic influences on working memory"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemoryIntegrationContract":
        """Deserialize from dictionary."""
        ref_data = data.get("working_memory_reference", {})
        if isinstance(ref_data, dict):
            working_memory_ref = WorkingMemoryReference.from_dict(ref_data)
        else:
            working_memory_ref = WorkingMemoryReference()
        
        context_data = data.get("working_memory_context")
        working_memory_context: Optional[WorkingMemoryContext] = None
        if isinstance(context_data, dict):
            working_memory_context = WorkingMemoryContext.from_dict(context_data)
        
        projection_data = data.get("working_memory_projection")
        working_memory_projection: Optional[WorkingMemoryProjection] = None
        if isinstance(projection_data, dict):
            working_memory_projection = WorkingMemoryProjection.from_dict(projection_data)
        
        relationships_data = data.get("relationships", [])
        relationships = tuple(
            WorkingMemoryRelationship.from_dict(r) if isinstance(r, dict) else r
            for r in relationships_data
        )
        
        influences_data = data.get("influences", [])
        influences = tuple(
            WorkingMemoryInfluence.from_dict(i) if isinstance(i, dict) else i
            for i in influences_data
        )
        
        return cls(
            contract_id=data.get("contract_id", "unnamed"),
            revision=data.get("revision", 1),
            working_memory_reference=working_memory_ref,
            working_memory_context=working_memory_context,
            working_memory_projection=working_memory_projection,
            relationships=relationships,
            influences=influences,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contract_id": self.contract_id,
            "revision": self.revision,
            "working_memory_reference": self.working_memory_reference.to_dict(),
            "working_memory_context": (
                self.working_memory_context.to_dict()
                if self.working_memory_context
                else None
            ),
            "working_memory_projection": (
                self.working_memory_projection.to_dict()
                if self.working_memory_projection
                else None
            ),
            "relationships": [r.to_dict() for r in self.relationships],
            "influences": [i.to_dict() for i in self.influences],
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the contract."""
        errors = []
        if not self.contract_id:
            errors.append("contract_id must be non-empty")
        if self.revision < 1:
            errors.append("revision must be >= 1")
        
        ref_valid, ref_errors = self.working_memory_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        if self.working_memory_context is not None:
            ctx_valid, ctx_errors = self.working_memory_context.validate()
            if not ctx_valid:
                errors.extend(ctx_errors)
        
        if self.working_memory_projection is not None:
            proj_valid, proj_errors = self.working_memory_projection.validate()
            if not proj_valid:
                errors.extend(proj_errors)
        
        for rel in self.relationships:
            rel_valid, rel_errors = rel.validate()
            if not rel_valid:
                errors.extend(rel_errors)
        
        for inf in self.influences:
            inf_valid, inf_errors = inf.validate()
            if not inf_valid:
                errors.extend(inf_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkingMemoryIntegrationContract:\n{error_str}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "WorkingMemoryReference",
    "WorkingMemoryContext",
    "WorkingMemoryProjection",
    "WorkingMemoryRelationship",
    "WorkingMemoryInfluence",
    "WorkingMemoryIntegrationContract",
]