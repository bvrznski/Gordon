# Oriented Network Motivation Integration Contracts
# ==================================================

"""
Motivation Network integration contracts for Phase 4.7.7.

OWNERSHIP:
    - Motivation Network owns: motivational valuation, persistence, priorities,
      intrinsic and extrinsic motivation
    - Oriented Network references: motivational context, projections, requirements

SEMANTIC INTEGRATION PRINCIPLES:
    - Never compute or fabricate motivation
    - Consume motivational projections only
    - Express requirements, never implement them

INTEGRATION LAWS:
    ORIENTED-COGNITIVE-INTEGRATION-LAW-003: Motivation Network remains sole owner
    ORIENTED-COGNITIVE-INTEGRATION-LAW-016: Integration shall never compute motivation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


# =============================================================================
# MOTIVATION REFERENCES - Semantic references to motivational concepts
# =============================================================================


@dataclass(frozen=True)
class MotivationReference:
    """
    Reference to a motivational concept without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every reference shall be explicit
        INTEGRATION-LAW-014: Every dependency shall be explicit
    """
    
    motivation_id: str = field(default="unnamed")
    """Unique identifier for the motivational concept being referenced"""
    
    reference_type: str = field(default="context")
    """Type of motivation reference (context, projection, requirement)"""
    
    valuation_level: Optional[str] = None
    """Valuation level hint (low, medium, high, critical - semantic only)"""
    
    persistence_hint: Optional[float] = None
    """Optional persistence duration hint in seconds"""
    
    @classmethod
    def context(cls, motivation_id: str) -> "MotivationReference":
        """
        Create a reference to motivational context.
        
        Args:
            motivation_id: ID of the motivational context
            
        Returns:
            New MotivationReference instance
        """
        return cls(motivation_id=motivation_id, reference_type="context")
    
    @classmethod
    def projection(cls, motivation_id: str) -> "MotivationReference":
        """
        Create a reference to a motivational projection.
        
        Args:
            motivation_id: ID of the motivational projection
            
        Returns:
            New MotivationReference instance
        """
        return cls(motivation_id=motivation_id, reference_type="projection")
    
    @classmethod
    def requirement(cls, motivation_id: str) -> "MotivationReference":
        """
        Create a reference to a motivational requirement.
        
        Args:
            motivation_id: ID of the motivational requirement
            
        Returns:
            New MotivationReference instance
        """
        return cls(motivation_id=motivation_id, reference_type="requirement")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "motivation_id": self.motivation_id,
            "reference_type": self.reference_type,
            "valuation_level": self.valuation_level,
            "persistence_hint": self.persistence_hint,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotivationReference":
        """Deserialize from dictionary."""
        return cls(
            motivation_id=data.get("motivation_id", "unnamed"),
            reference_type=data.get("reference_type", "context"),
            valuation_level=data.get("valuation_level"),
            persistence_hint=data.get("persistence_hint"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the reference."""
        errors = []
        if not self.motivation_id:
            errors.append("motivation_id must be non-empty")
        if self.reference_type not in ("context", "projection", "requirement"):
            errors.append(f"invalid reference_type: {self.reference_type}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid MotivationReference:\n{error_str}")


# =============================================================================
# MOTIVATION CONTEXT - Immutable motivational state projection
# =============================================================================


@dataclass(frozen=True)
class MotivationContext:
    """
    Projection of current motivational state without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-016: Integration shall never compute motivation
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
    """
    
    context_id: str = field(default="unnamed")
    """Unique identifier for this motivational context"""
    
    active_motivations: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently active motivations"""
    
    valuation_map: Dict[str, float] = field(default_factory=dict)
    """Valuation levels per motivation (semantic only)"""
    
    persistence_seconds: Optional[float] = None
    """Estimated total persistence duration"""
    
    intrinsic_motivation_ratio: Optional[float] = None
    """Ratio of intrinsic to extrinsic motivation (0.0 to 1.0)"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotivationContext":
        """Deserialize from dictionary."""
        active_mocks = tuple(data.get("active_motivations", []))
        valuation = dict(data.get("valuation_map", {}))
        
        return cls(
            context_id=data.get("context_id", "unnamed"),
            active_motivations=active_mocks,
            valuation_map=valuation,
            persistence_seconds=data.get("persistence_seconds"),
            intrinsic_motivation_ratio=data.get("intrinsic_motivation_ratio"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "context_id": self.context_id,
            "active_motivations": list(self.active_motivations),
            "valuation_map": dict(self.valuation_map),
            "persistence_seconds": self.persistence_seconds,
            "intrinsic_motivation_ratio": self.intrinsic_motivation_ratio,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the context."""
        errors = []
        if not self.context_id:
            errors.append("context_id must be non-empty")
        for value in self.valuation_map.values():
            if not (0.0 <= value <= 1.0):
                errors.append(f"invalid valuation value: {value}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid MotivationContext:\n{error_str}")


# =============================================================================
# MOTIVATION PROJECTION - Information about motivational state
# =============================================================================


@dataclass(frozen=True)
class MotivationProjection:
    """
    Projection of motivational information without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-016: Integration shall never compute motivation
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    projection_id: str = field(default="unnamed")
    """Unique identifier for this projection"""
    
    context: MotivationContext = field(default_factory=MotivationContext)
    """Current motivational context"""
    
    available_drive_capacity: float = field(default=1.0)
    """Available drive capacity as ratio (0.0 to 1.0)"""
    
    estimated_sustained_seconds: Optional[float] = None
    """Estimated duration of current drive state"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotivationProjection":
        """Deserialize from dictionary."""
        context_data = data.get("context", {})
        if isinstance(context_data, dict):
            context = MotivationContext.from_dict(context_data)
        else:
            context = MotivationContext()
        
        return cls(
            projection_id=data.get("projection_id", "unnamed"),
            context=context,
            available_drive_capacity=float(data.get("available_drive_capacity", 1.0)),
            estimated_sustained_seconds=data.get("estimated_sustained_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "projection_id": self.projection_id,
            "context": self.context.to_dict(),
            "available_drive_capacity": self.available_drive_capacity,
            "estimated_sustained_seconds": self.estimated_sustained_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the projection."""
        errors = []
        if not self.projection_id:
            errors.append("projection_id must be non-empty")
        if not (0.0 <= self.available_drive_capacity <= 1.0):
            errors.append(f"invalid capacity value: {self.available_drive_capacity}")
        
        context_valid, context_errors = self.context.validate()
        if not context_valid:
            errors.extend(context_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid MotivationProjection:\n{error_str}")


# =============================================================================
# MOTIVATION RELATIONSHIP - Semantic relationship to motivation
# =============================================================================


@dataclass(frozen=True)
class MotivationRelationship:
    """
    Semantic relationship between orientation and motivation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every relationship shall be explicit
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    relationship_id: str = field(default="unnamed")
    """Unique identifier for this relationship"""
    
    motivation_reference: MotivationReference = field(
        default_factory=lambda: MotivationReference()
    )
    """Reference to the motivation being related to"""
    
    relationship_type: str = field(default="consume")
    """Type of relationship (consume, reference, require)"""
    
    purpose: str = field(default="")
    """Semantic purpose of this relationship"""
    
    @classmethod
    def consume(cls, motivation_id: str, purpose: str = "") -> "MotivationRelationship":
        """
        Create a consumption relationship.
        
        Args:
            motivation_id: ID of the motivation to consume
            purpose: Semantic purpose
            
        Returns:
            New MotivationRelationship instance
        """
        return cls(
            relationship_id=f"consume_{motivation_id}",
            motivation_reference=MotivationReference(motivation_id, "context"),
            relationship_type="consume",
            purpose=purpose,
        )
    
    @classmethod
    def reference(cls, motivation_id: str, purpose: str = "") -> "MotivationRelationship":
        """
        Create a reference relationship.
        
        Args:
            motivation_id: ID of the motivation to reference
            purpose: Semantic purpose
            
        Returns:
            New MotivationRelationship instance
        """
        return cls(
            relationship_id=f"reference_{motivation_id}",
            motivation_reference=MotivationReference(motivation_id, "projection"),
            relationship_type="reference",
            purpose=purpose,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "relationship_id": self.relationship_id,
            "motivation_reference": self.motivation_reference.to_dict(),
            "relationship_type": self.relationship_type,
            "purpose": self.purpose,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotivationRelationship":
        """Deserialize from dictionary."""
        ref_data = data.get("motivation_reference", {})
        if isinstance(ref_data, dict):
            motivation_ref = MotivationReference.from_dict(ref_data)
        else:
            motivation_ref = MotivationReference()
        
        return cls(
            relationship_id=data.get("relationship_id", "unnamed"),
            motivation_reference=motivation_ref,
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
        
        ref_valid, ref_errors = self.motivation_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid MotivationRelationship:\n{error_str}")


# =============================================================================
# MOTIVATION INFLUENCE - Semantic influence on motivation
# =============================================================================


@dataclass(frozen=True)
class MotivationInfluence:
    """
    Semantic influence that orientation may have on motivation.
    
    DESCRIBES what influence the Oriented Network can express without owning
    or implementing it. This is NOT a directive, only a semantic expectation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-016: Integration shall never compute motivation
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    influence_id: str = field(default="unnamed")
    """Unique identifier for this influence"""
    
    influence_type: str = field(default="requirement")
    """Type of influence (requirement, expectation, suggestion)"""
    
    target_motivation: Optional[str] = None
    """Target motivation ID if applicable"""
    
    expected_state: Dict[str, Any] = field(default_factory=dict)
    """Expected state description (semantic only)"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotivationInfluence":
        """Deserialize from dictionary."""
        return cls(
            influence_id=data.get("influence_id", "unnamed"),
            influence_type=data.get("influence_type", "requirement"),
            target_motivation=data.get("target_motivation"),
            expected_state=dict(data.get("expected_state", {})),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "influence_id": self.influence_id,
            "influence_type": self.influence_type,
            "target_motivation": self.target_motivation,
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
            raise ValueError(f"Invalid MotivationInfluence:\n{error_str}")


# =============================================================================
# MOTIVATION INTEGRATION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class MotivationIntegrationContract:
    """
    Complete integration contract for Motivation Network.
    
    Combines all semantic elements needed for orientation to interact with
    the motivational system without ownership or implementation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-003: Motivation Network remains sole owner
        INTEGRATION-LAW-016: Integration shall never compute motivation
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
        INTEGRATION-LAW-027: Deterministic serialization support
    """
    
    contract_id: str = field(default="unnamed")
    """Unique identifier for this integration contract"""
    
    revision: int = field(default=1)
    """Semantic revision number"""
    
    motivation_reference: MotivationReference = field(
        default_factory=lambda: MotivationReference()
    )
    """Primary motivation reference"""
    
    motivation_context: Optional[MotivationContext] = None
    """Current motivational context (if available)"""
    
    motivation_projection: Optional[MotivationProjection] = None
    """Motivational projection (if available)"""
    
    relationships: Tuple[MotivationRelationship, ...] = field(default_factory=tuple)
    """Semantic relationships to motivation"""
    
    influences: Tuple[MotivationInfluence, ...] = field(default_factory=tuple)
    """Semantic influences on motivation"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotivationIntegrationContract":
        """Deserialize from dictionary."""
        ref_data = data.get("motivation_reference", {})
        if isinstance(ref_data, dict):
            motivation_ref = MotivationReference.from_dict(ref_data)
        else:
            motivation_ref = MotivationReference()
        
        context_data = data.get("motivation_context")
        motivation_context: Optional[MotivationContext] = None
        if isinstance(context_data, dict):
            motivation_context = MotivationContext.from_dict(context_data)
        
        projection_data = data.get("motivation_projection")
        motivation_projection: Optional[MotivationProjection] = None
        if isinstance(projection_data, dict):
            motivation_projection = MotivationProjection.from_dict(projection_data)
        
        relationships_data = data.get("relationships", [])
        relationships = tuple(
            MotivationRelationship.from_dict(r) if isinstance(r, dict) else r
            for r in relationships_data
        )
        
        influences_data = data.get("influences", [])
        influences = tuple(
            MotivationInfluence.from_dict(i) if isinstance(i, dict) else i
            for i in influences_data
        )
        
        return cls(
            contract_id=data.get("contract_id", "unnamed"),
            revision=data.get("revision", 1),
            motivation_reference=motivation_ref,
            motivation_context=motivation_context,
            motivation_projection=motivation_projection,
            relationships=relationships,
            influences=influences,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contract_id": self.contract_id,
            "revision": self.revision,
            "motivation_reference": self.motivation_reference.to_dict(),
            "motivation_context": (
                self.motivation_context.to_dict()
                if self.motivation_context
                else None
            ),
            "motivation_projection": (
                self.motivation_projection.to_dict()
                if self.motivation_projection
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
        
        ref_valid, ref_errors = self.motivation_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        if self.motivation_context is not None:
            ctx_valid, ctx_errors = self.motivation_context.validate()
            if not ctx_valid:
                errors.extend(ctx_errors)
        
        if self.motivation_projection is not None:
            proj_valid, proj_errors = self.motivation_projection.validate()
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
            raise ValueError(f"Invalid MotivationIntegrationContract:\n{error_str}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MotivationReference",
    "MotivationContext",
    "MotivationProjection",
    "MotivationRelationship",
    "MotivationInfluence",
    "MotivationIntegrationContract",
]