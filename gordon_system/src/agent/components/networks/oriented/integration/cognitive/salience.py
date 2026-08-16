# Oriented Network Salience Integration Contracts
# ===============================================

"""
Salience Network integration contracts for Phase 4.7.7.

OWNERSHIP:
    - Salience Network owns: relevance computation, novelty detection,
      significance estimation, priority emergence
    - Oriented Network references: salience context, projections, requirements

SEMANTIC INTEGRATION PRINCIPLES:
    - Never compute or estimate salience
    - Consume salience projections only
    - Express requirements, never implement them

INTEGRATION LAWS:
    ORIENTED-COGNITIVE-INTEGRATION-LAW-004: Salience Network remains sole owner
    ORIENTED-COGNITIVE-INTEGRATION-LAW-017: Integration shall never compute salience
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


# =============================================================================
# SALIENCE REFERENCES - Semantic references to salient concepts
# =============================================================================


@dataclass(frozen=True)
class SalienceReference:
    """
    Reference to a salient concept without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every reference shall be explicit
        INTEGRATION-LAW-014: Every dependency shall be explicit
    """
    
    salience_id: str = field(default="unnamed")
    """Unique identifier for the salient concept being referenced"""
    
    reference_type: str = field(default="context")
    """Type of salience reference (context, projection, requirement)"""
    
    priority_level: Optional[str] = None
    """Priority level hint (low, medium, high, critical - semantic only)"""
    
    relevance_score: Optional[float] = None
    """Relevance score hint (0.0 to 1.0 - semantic only)"""
    
    @classmethod
    def context(cls, salience_id: str) -> "SalienceReference":
        """
        Create a reference to salient context.
        
        Args:
            salience_id: ID of the salient context
            
        Returns:
            New SalienceReference instance
        """
        return cls(salience_id=salience_id, reference_type="context")
    
    @classmethod
    def projection(cls, salience_id: str) -> "SalienceReference":
        """
        Create a reference to a salient projection.
        
        Args:
            salience_id: ID of the salient projection
            
        Returns:
            New SalienceReference instance
        """
        return cls(salience_id=salience_id, reference_type="projection")
    
    @classmethod
    def requirement(cls, salience_id: str) -> "SalienceReference":
        """
        Create a reference to a salience requirement.
        
        Args:
            salience_id: ID of the salience requirement
            
        Returns:
            New SalienceReference instance
        """
        return cls(salience_id=salience_id, reference_type="requirement")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "salience_id": self.salience_id,
            "reference_type": self.reference_type,
            "priority_level": self.priority_level,
            "relevance_score": self.relevance_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalienceReference":
        """Deserialize from dictionary."""
        return cls(
            salience_id=data.get("salience_id", "unnamed"),
            reference_type=data.get("reference_type", "context"),
            priority_level=data.get("priority_level"),
            relevance_score=data.get("relevance_score"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the reference."""
        errors = []
        if not self.salience_id:
            errors.append("salience_id must be non-empty")
        if self.reference_type not in ("context", "projection", "requirement"):
            errors.append(f"invalid reference_type: {self.reference_type}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid SalienceReference:\n{error_str}")


# =============================================================================
# SALIENCE CONTEXT - Immutable salient state projection
# =============================================================================


@dataclass(frozen=True)
class SalienceContext:
    """
    Projection of current salient state without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-017: Integration shall never compute salience
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
    """
    
    context_id: str = field(default="unnamed")
    """Unique identifier for this salient context"""
    
    salient_items: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently salient items"""
    
    significance_map: Dict[str, float] = field(default_factory=dict)
    """Significance levels per item (semantic only)"""
    
    novelty_count: int = 0
    """Count of novel items in current context"""
    
    estimated_priority_seconds: Optional[float] = None
    """Estimated priority duration"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalienceContext":
        """Deserialize from dictionary."""
        salient = tuple(data.get("salient_items", []))
        significance = dict(data.get("significance_map", {}))
        
        return cls(
            context_id=data.get("context_id", "unnamed"),
            salient_items=salient,
            significance_map=significance,
            novelty_count=int(data.get("novelty_count", 0)),
            estimated_priority_seconds=data.get("estimated_priority_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "context_id": self.context_id,
            "salient_items": list(self.salient_items),
            "significance_map": dict(self.significance_map),
            "novelty_count": self.novelty_count,
            "estimated_priority_seconds": self.estimated_priority_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the context."""
        errors = []
        if not self.context_id:
            errors.append("context_id must be non-empty")
        for value in self.significance_map.values():
            if not (0.0 <= value <= 1.0):
                errors.append(f"invalid significance value: {value}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid SalienceContext:\n{error_str}")


# =============================================================================
# SALIENCE PROJECTION - Information about salient state
# =============================================================================


@dataclass(frozen=True)
class SalienceProjection:
    """
    Projection of salient information without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-017: Integration shall never compute salience
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    projection_id: str = field(default="unnamed")
    """Unique identifier for this projection"""
    
    context: SalienceContext = field(default_factory=SalienceContext)
    """Current salient context"""
    
    available_salience_capacity: float = field(default=1.0)
    """Available salience capacity as ratio (0.0 to 1.0)"""
    
    estimated_stable_seconds: Optional[float] = None
    """Estimated duration of current salient state"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalienceProjection":
        """Deserialize from dictionary."""
        context_data = data.get("context", {})
        if isinstance(context_data, dict):
            context = SalienceContext.from_dict(context_data)
        else:
            context = SalienceContext()
        
        return cls(
            projection_id=data.get("projection_id", "unnamed"),
            context=context,
            available_salience_capacity=float(data.get("available_salience_capacity", 1.0)),
            estimated_stable_seconds=data.get("estimated_stable_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "projection_id": self.projection_id,
            "context": self.context.to_dict(),
            "available_salience_capacity": self.available_salience_capacity,
            "estimated_stable_seconds": self.estimated_stable_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the projection."""
        errors = []
        if not self.projection_id:
            errors.append("projection_id must be non-empty")
        if not (0.0 <= self.available_salience_capacity <= 1.0):
            errors.append(f"invalid capacity value: {self.available_salience_capacity}")
        
        context_valid, context_errors = self.context.validate()
        if not context_valid:
            errors.extend(context_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid SalienceProjection:\n{error_str}")


# =============================================================================
# SALIENCE RELATIONSHIP - Semantic relationship to salience
# =============================================================================


@dataclass(frozen=True)
class SalienceRelationship:
    """
    Semantic relationship between orientation and salience.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every relationship shall be explicit
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    relationship_id: str = field(default="unnamed")
    """Unique identifier for this relationship"""
    
    salience_reference: SalienceReference = field(
        default_factory=lambda: SalienceReference()
    )
    """Reference to the salience being related to"""
    
    relationship_type: str = field(default="consume")
    """Type of relationship (consume, reference, require)"""
    
    purpose: str = field(default="")
    """Semantic purpose of this relationship"""
    
    @classmethod
    def consume(cls, salience_id: str, purpose: str = "") -> "SalienceRelationship":
        """
        Create a consumption relationship.
        
        Args:
            salience_id: ID of the salience to consume
            purpose: Semantic purpose
            
        Returns:
            New SalienceRelationship instance
        """
        return cls(
            relationship_id=f"consume_{salience_id}",
            salience_reference=SalienceReference(salience_id, "context"),
            relationship_type="consume",
            purpose=purpose,
        )
    
    @classmethod
    def reference(cls, salience_id: str, purpose: str = "") -> "SalienceRelationship":
        """
        Create a reference relationship.
        
        Args:
            salience_id: ID of the salience to reference
            purpose: Semantic purpose
            
        Returns:
            New SalienceRelationship instance
        """
        return cls(
            relationship_id=f"reference_{salience_id}",
            salience_reference=SalienceReference(salience_id, "projection"),
            relationship_type="reference",
            purpose=purpose,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "relationship_id": self.relationship_id,
            "salience_reference": self.salience_reference.to_dict(),
            "relationship_type": self.relationship_type,
            "purpose": self.purpose,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalienceRelationship":
        """Deserialize from dictionary."""
        ref_data = data.get("salience_reference", {})
        if isinstance(ref_data, dict):
            salience_ref = SalienceReference.from_dict(ref_data)
        else:
            salience_ref = SalienceReference()
        
        return cls(
            relationship_id=data.get("relationship_id", "unnamed"),
            salience_reference=salience_ref,
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
        
        ref_valid, ref_errors = self.salience_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid SalienceRelationship:\n{error_str}")


# =============================================================================
# SALIENCE INFLUENCE - Semantic influence on salience
# =============================================================================


@dataclass(frozen=True)
class SalienceInfluence:
    """
    Semantic influence that orientation may have on salience.
    
    DESCRIBES what influence the Oriented Network can express without owning
    or implementing it. This is NOT a directive, only a semantic expectation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-017: Integration shall never compute salience
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    influence_id: str = field(default="unnamed")
    """Unique identifier for this influence"""
    
    influence_type: str = field(default="requirement")
    """Type of influence (requirement, expectation, suggestion)"""
    
    target_salience: Optional[str] = None
    """Target salience ID if applicable"""
    
    expected_state: Dict[str, Any] = field(default_factory=dict)
    """Expected state description (semantic only)"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalienceInfluence":
        """Deserialize from dictionary."""
        return cls(
            influence_id=data.get("influence_id", "unnamed"),
            influence_type=data.get("influence_type", "requirement"),
            target_salience=data.get("target_salience"),
            expected_state=dict(data.get("expected_state", {})),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "influence_id": self.influence_id,
            "influence_type": self.influence_type,
            "target_salience": self.target_salience,
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
            raise ValueError(f"Invalid SalienceInfluence:\n{error_str}")


# =============================================================================
# SALIENCE INTEGRATION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class SalienceIntegrationContract:
    """
    Complete integration contract for Salience Network.
    
    Combines all semantic elements needed for orientation to interact with
    the salient system without ownership or implementation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-004: Salience Network remains sole owner
        INTEGRATION-LAW-017: Integration shall never compute salience
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
        INTEGRATION-LAW-027: Deterministic serialization support
    """
    
    contract_id: str = field(default="unnamed")
    """Unique identifier for this integration contract"""
    
    revision: int = field(default=1)
    """Semantic revision number"""
    
    salience_reference: SalienceReference = field(
        default_factory=lambda: SalienceReference()
    )
    """Primary salience reference"""
    
    salience_context: Optional[SalienceContext] = None
    """Current salient context (if available)"""
    
    salience_projection: Optional[SalienceProjection] = None
    """Salient projection (if available)"""
    
    relationships: Tuple[SalienceRelationship, ...] = field(default_factory=tuple)
    """Semantic relationships to salience"""
    
    influences: Tuple[SalienceInfluence, ...] = field(default_factory=tuple)
    """Semantic influences on salience"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalienceIntegrationContract":
        """Deserialize from dictionary."""
        ref_data = data.get("salience_reference", {})
        if isinstance(ref_data, dict):
            salience_ref = SalienceReference.from_dict(ref_data)
        else:
            salience_ref = SalienceReference()
        
        context_data = data.get("salience_context")
        salience_context: Optional[SalienceContext] = None
        if isinstance(context_data, dict):
            salience_context = SalienceContext.from_dict(context_data)
        
        projection_data = data.get("salience_projection")
        salience_projection: Optional[SalienceProjection] = None
        if isinstance(projection_data, dict):
            salience_projection = SalienceProjection.from_dict(projection_data)
        
        relationships_data = data.get("relationships", [])
        relationships = tuple(
            SalienceRelationship.from_dict(r) if isinstance(r, dict) else r
            for r in relationships_data
        )
        
        influences_data = data.get("influences", [])
        influences = tuple(
            SalienceInfluence.from_dict(i) if isinstance(i, dict) else i
            for i in influences_data
        )
        
        return cls(
            contract_id=data.get("contract_id", "unnamed"),
            revision=data.get("revision", 1),
            salience_reference=salience_ref,
            salience_context=salience_context,
            salience_projection=salience_projection,
            relationships=relationships,
            influences=influences,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contract_id": self.contract_id,
            "revision": self.revision,
            "salience_reference": self.salience_reference.to_dict(),
            "salience_context": (
                self.salience_context.to_dict()
                if self.salience_context
                else None
            ),
            "salience_projection": (
                self.salience_projection.to_dict()
                if self.salience_projection
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
        
        ref_valid, ref_errors = self.salience_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        if self.salience_context is not None:
            ctx_valid, ctx_errors = self.salience_context.validate()
            if not ctx_valid:
                errors.extend(ctx_errors)
        
        if self.salience_projection is not None:
            proj_valid, proj_errors = self.salience_projection.validate()
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
            raise ValueError(f"Invalid SalienceIntegrationContract:\n{error_str}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "SalienceReference",
    "SalienceContext",
    "SalienceProjection",
    "SalienceRelationship",
    "SalienceInfluence",
    "SalienceIntegrationContract",
]