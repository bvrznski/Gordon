# Oriented Network Attention Integration Contracts
# ================================================

"""
Attention Network integration contracts for Phase 4.7.7.

OWNERSHIP:
    - Attention Network owns: attentional allocation, control, switching, persistence
    - Oriented Network references: attention context, projections, requirements
    
SEMANTIC INTEGRATION PRINCIPLES:
    - Never allocate or reprioritize
    - Consume attentional context only
    - Express requirements, never implement them

INTEGRATION LAWS:
    ORIENTED-COGNITIVE-INTEGRATION-LAW-002: Attention Network remains sole owner
    ORIENTED-COGNITIVE-INTEGRATION-LAW-015: Integration shall never allocate attention
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


# =============================================================================
# ATTENTION REFERENCES - Semantic references to attentional concepts
# =============================================================================


@dataclass(frozen=True)
class AttentionReference:
    """
    Reference to an attentional concept without ownership.
    
    Used when the Oriented Network needs to reference attentional state
    or requirements without owning or modifying them.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every reference shall be explicit
        INTEGRATION-LAW-014: Every dependency shall be explicit
    """
    
    attention_id: str = field(default="unnamed")
    """Unique identifier for the attentional concept being referenced"""
    
    reference_type: str = field(default="context")
    """Type of attention reference (context, projection, requirement)"""
    
    priority_level: Optional[str] = None
    """Priority level hint (low, medium, high, critical - semantic only)"""
    
    duration_hint_seconds: Optional[float] = None
    """Optional duration hint for sustained attention needs"""
    
    @classmethod
    def context(cls, attention_id: str) -> "AttentionReference":
        """
        Create a reference to attentional context.
        
        Args:
            attention_id: ID of the attentional context
            
        Returns:
            New AttentionReference instance
        """
        return cls(attention_id=attention_id, reference_type="context")
    
    @classmethod
    def projection(cls, attention_id: str) -> "AttentionReference":
        """
        Create a reference to an attentional projection.
        
        Args:
            attention_id: ID of the attentional projection
            
        Returns:
            New AttentionReference instance
        """
        return cls(attention_id=attention_id, reference_type="projection")
    
    @classmethod
    def requirement(cls, attention_id: str) -> "AttentionReference":
        """
        Create a reference to an attentional requirement.
        
        Args:
            attention_id: ID of the attentional requirement
            
        Returns:
            New AttentionReference instance
        """
        return cls(attention_id=attention_id, reference_type="requirement")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "attention_id": self.attention_id,
            "reference_type": self.reference_type,
            "priority_level": self.priority_level,
            "duration_hint_seconds": self.duration_hint_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionReference":
        """Deserialize from dictionary."""
        return cls(
            attention_id=data.get("attention_id", "unnamed"),
            reference_type=data.get("reference_type", "context"),
            priority_level=data.get("priority_level"),
            duration_hint_seconds=data.get("duration_hint_seconds"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the reference."""
        errors = []
        if not self.attention_id:
            errors.append("attention_id must be non-empty")
        if self.reference_type not in ("context", "projection", "requirement"):
            errors.append(f"invalid reference_type: {self.reference_type}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid AttentionReference:\n{error_str}")


# =============================================================================
# ATTENTION CONTEXT - Immutable attentional state projection
# =============================================================================


@dataclass(frozen=True)
class AttentionContext:
    """
    Projection of current attentional state without ownership.
    
    The Oriented Network consumes this context but never modifies it.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-015: Integration shall never allocate attention
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
    """
    
    context_id: str = field(default="unnamed")
    """Unique identifier for this attentional context"""
    
    active_attention_targets: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently focused attention targets"""
    
    attention_allocation: Dict[str, float] = field(default_factory=dict)
    """Current allocation percentages per target (semantic only)"""
    
    attention_control_mode: str = field(default="manual")
    """Mode of attention control (manual, automatic, hybrid)"""
    
    last_attention_switch_utc: Optional[str] = None
    """ISO timestamp of the last attention switch (if known)"""
    
    estimated_sustained_duration_seconds: Optional[float] = None
    """Estimated duration of current focus period"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionContext":
        """Deserialize from dictionary."""
        active_targets = tuple(data.get("active_attention_targets", []))
        allocation = dict(data.get("attention_allocation", {}))
        
        return cls(
            context_id=data.get("context_id", "unnamed"),
            active_attention_targets=active_targets,
            attention_allocation=allocation,
            attention_control_mode=data.get("attention_control_mode", "manual"),
            last_attention_switch_utc=data.get("last_attention_switch_utc"),
            estimated_sustained_duration_seconds=data.get("estimated_sustained_duration_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "context_id": self.context_id,
            "active_attention_targets": list(self.active_attention_targets),
            "attention_allocation": dict(self.attention_allocation),
            "attention_control_mode": self.attention_control_mode,
            "last_attention_switch_utc": self.last_attention_switch_utc,
            "estimated_sustained_duration_seconds": self.estimated_sustained_duration_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the context."""
        errors = []
        if not self.context_id:
            errors.append("context_id must be non-empty")
        for target, allocation in self.attention_allocation.items():
            if not isinstance(target, str):
                errors.append(f"invalid target type: {type(target)}")
            if not (0.0 <= allocation <= 1.0):
                errors.append(f"invalid allocation value: {allocation}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid AttentionContext:\n{error_str}")
    
    @property
    def total_allocation(self) -> float:
        """Calculate total attention allocation (semantic only)."""
        return sum(self.attention_allocation.values())
    
    def has_target(self, target_id: str) -> bool:
        """
        Check if a target is currently being attended.
        
        Args:
            target_id: ID of the target to check
            
        Returns:
            True if the target is in active_attention_targets
        """
        return target_id in self.active_attention_targets


# =============================================================================
# ATTENTION PROJECTION - Information about attentional state
# =============================================================================


@dataclass(frozen=True)
class AttentionProjection:
    """
    Projection of attentional information without ownership.
    
    Contains information about attention that may influence orientation decisions.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-015: Integration shall never allocate attention
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    projection_id: str = field(default="unnamed")
    """Unique identifier for this projection"""
    
    context: AttentionContext = field(default_factory=AttentionContext)
    """Current attentional context"""
    
    available_attentional_capacity: float = field(default=1.0)
    """Available capacity as ratio (0.0 to 1.0)"""
    
    switch_cost_seconds: Optional[float] = None
    """Estimated time cost for attention switching"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionProjection":
        """Deserialize from dictionary."""
        context_data = data.get("context", {})
        if isinstance(context_data, dict):
            context = AttentionContext.from_dict(context_data)
        else:
            context = AttentionContext()
        
        return cls(
            projection_id=data.get("projection_id", "unnamed"),
            context=context,
            available_attentional_capacity=float(data.get("available_attentional_capacity", 1.0)),
            switch_cost_seconds=data.get("switch_cost_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "projection_id": self.projection_id,
            "context": self.context.to_dict(),
            "available_attentional_capacity": self.available_attentional_capacity,
            "switch_cost_seconds": self.switch_cost_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the projection."""
        errors = []
        if not self.projection_id:
            errors.append("projection_id must be non-empty")
        if not (0.0 <= self.available_attentional_capacity <= 1.0):
            errors.append(f"invalid capacity value: {self.available_attentional_capacity}")
        
        context_valid, context_errors = self.context.validate()
        if not context_valid:
            errors.extend(context_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid AttentionProjection:\n{error_str}")


# =============================================================================
# ATTENTION RELATIONSHIP - Semantic relationship to attention
# =============================================================================


@dataclass(frozen=True)
class AttentionRelationship:
    """
    Semantic relationship between orientation and attention.
    
    Defines how the Oriented Network interacts with attentional processes.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every relationship shall be explicit
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    relationship_id: str = field(default="unnamed")
    """Unique identifier for this relationship"""
    
    attention_reference: AttentionReference = field(
        default_factory=lambda: AttentionReference()
    )
    """Reference to the attention being related to"""
    
    relationship_type: str = field(default="consume")
    """Type of relationship (consume, reference, require)"""
    
    purpose: str = field(default="")
    """Semantic purpose of this relationship"""
    
    @classmethod
    def consume(cls, attention_id: str, purpose: str = "") -> "AttentionRelationship":
        """
        Create a consumption relationship.
        
        Args:
            attention_id: ID of the attention to consume
            purpose: Semantic purpose
            
        Returns:
            New AttentionRelationship instance
        """
        return cls(
            relationship_id=f"consume_{attention_id}",
            attention_reference=AttentionReference(attention_id, "context"),
            relationship_type="consume",
            purpose=purpose,
        )
    
    @classmethod
    def reference(cls, attention_id: str, purpose: str = "") -> "AttentionRelationship":
        """
        Create a reference relationship.
        
        Args:
            attention_id: ID of the attention to reference
            purpose: Semantic purpose
            
        Returns:
            New AttentionRelationship instance
        """
        return cls(
            relationship_id=f"reference_{attention_id}",
            attention_reference=AttentionReference(attention_id, "projection"),
            relationship_type="reference",
            purpose=purpose,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "relationship_id": self.relationship_id,
            "attention_reference": self.attention_reference.to_dict(),
            "relationship_type": self.relationship_type,
            "purpose": self.purpose,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionRelationship":
        """Deserialize from dictionary."""
        ref_data = data.get("attention_reference", {})
        if isinstance(ref_data, dict):
            attention_ref = AttentionReference.from_dict(ref_data)
        else:
            attention_ref = AttentionReference()
        
        return cls(
            relationship_id=data.get("relationship_id", "unnamed"),
            attention_reference=attention_ref,
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
        
        ref_valid, ref_errors = self.attention_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid AttentionRelationship:\n{error_str}")


# =============================================================================
# ATTENTION INFLUENCE - Semantic influence on attention
# =============================================================================


@dataclass(frozen=True)
class AttentionInfluence:
    """
    Semantic influence that orientation may have on attention.
    
    Describes what influence the Oriented Network can express without owning
    or implementing it. This is NOT a directive, only a semantic expectation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-015: Integration shall never allocate attention
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    influence_id: str = field(default="unnamed")
    """Unique identifier for this influence"""
    
    influence_type: str = field(default="requirement")
    """Type of influence (requirement, expectation, suggestion)"""
    
    target_attention: Optional[str] = None
    """Target attention ID if applicable"""
    
    expected_state: Dict[str, Any] = field(default_factory=dict)
    """Expected state description (semantic only)"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionInfluence":
        """Deserialize from dictionary."""
        return cls(
            influence_id=data.get("influence_id", "unnamed"),
            influence_type=data.get("influence_type", "requirement"),
            target_attention=data.get("target_attention"),
            expected_state=dict(data.get("expected_state", {})),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "influence_id": self.influence_id,
            "influence_type": self.influence_type,
            "target_attention": self.target_attention,
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
            raise ValueError(f"Invalid AttentionInfluence:\n{error_str}")


# =============================================================================
# ATTENTION INTEGRATION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class AttentionIntegrationContract:
    """
    Complete integration contract for Attention Network.
    
    Combines all semantic elements needed for orientation to interact with
    the attentional system without ownership or implementation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-002: Attention Network remains sole owner
        INTEGRATION-LAW-015: Integration shall never allocate attention
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
        INTEGRATION-LAW-027: Deterministic serialization support
    """
    
    contract_id: str = field(default="unnamed")
    """Unique identifier for this integration contract"""
    
    revision: int = field(default=1)
    """Semantic revision number"""
    
    attention_reference: AttentionReference = field(
        default_factory=lambda: AttentionReference()
    )
    """Primary attention reference"""
    
    attention_context: Optional[AttentionContext] = None
    """Current attentional context (if available)"""
    
    attention_projection: Optional[AttentionProjection] = None
    """Attentional projection (if available)"""
    
    relationships: Tuple[AttentionRelationship, ...] = field(default_factory=tuple)
    """Semantic relationships to attention"""
    
    influences: Tuple[AttentionInfluence, ...] = field(default_factory=tuple)
    """Semantic influences on attention"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionIntegrationContract":
        """Deserialize from dictionary."""
        ref_data = data.get("attention_reference", {})
        if isinstance(ref_data, dict):
            attention_ref = AttentionReference.from_dict(ref_data)
        else:
            attention_ref = AttentionReference()
        
        context_data = data.get("attention_context")
        attention_context: Optional[AttentionContext] = None
        if isinstance(context_data, dict):
            attention_context = AttentionContext.from_dict(context_data)
        
        projection_data = data.get("attention_projection")
        attention_projection: Optional[AttentionProjection] = None
        if isinstance(projection_data, dict):
            attention_projection = AttentionProjection.from_dict(projection_data)
        
        relationships_data = data.get("relationships", [])
        relationships = tuple(
            AttentionRelationship.from_dict(r) if isinstance(r, dict) else r
            for r in relationships_data
        )
        
        influences_data = data.get("influences", [])
        influences = tuple(
            AttentionInfluence.from_dict(i) if isinstance(i, dict) else i
            for i in influences_data
        )
        
        return cls(
            contract_id=data.get("contract_id", "unnamed"),
            revision=data.get("revision", 1),
            attention_reference=attention_ref,
            attention_context=attention_context,
            attention_projection=attention_projection,
            relationships=relationships,
            influences=influences,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contract_id": self.contract_id,
            "revision": self.revision,
            "attention_reference": self.attention_reference.to_dict(),
            "attention_context": (
                self.attention_context.to_dict()
                if self.attention_context
                else None
            ),
            "attention_projection": (
                self.attention_projection.to_dict()
                if self.attention_projection
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
        
        ref_valid, ref_errors = self.attention_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        if self.attention_context is not None:
            ctx_valid, ctx_errors = self.attention_context.validate()
            if not ctx_valid:
                errors.extend(ctx_errors)
        
        if self.attention_projection is not None:
            proj_valid, proj_errors = self.attention_projection.validate()
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
            raise ValueError(f"Invalid AttentionIntegrationContract:\n{error_str}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AttentionReference",
    "AttentionContext",
    "AttentionProjection",
    "AttentionRelationship",
    "AttentionInfluence",
    "AttentionIntegrationContract",
]