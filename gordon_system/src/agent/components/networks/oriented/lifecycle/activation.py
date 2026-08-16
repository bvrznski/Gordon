# Oriented Network Activation Models - Phase 4.7.9
# ================================================

"""
Activation semantics for semantic orientation evolution.

SEMANTIC ROLE:
    - Represents semantic availability of Orientation
    - Never owns runtime execution
    
ACTIVATION CONCEPTS:
    Context        - The environment in which activation occurs
    Requirement    - Conditions that must be satisfied for activation
    Relationship   - Dependencies between orientations and activators
    Projection     - Expected state after activation
    Reference      - How orientations reference their activation source
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# ACTIVATION CONTEXT
# =============================================================================

@dataclass(frozen=True)
class ActivationContext:
    """
    The environment in which orientation activation occurs.
    
    SEMANTIC ROLE:
        - Represents semantic readiness conditions for orientation
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Immutable: Frozen dataclass
        - Semantic: Describes state, not behavior
        - Deterministic: Same inputs produce same outputs
        
    OWNERSHIP:
        - Owns: Activation context and readiness indicators
        - Never owns: Execution engines, schedulers, resources
    """
    
    context_id: str
    readiness_level: float = field(default=1.0)  # 0.0 to 1.0
    activation_environment: dict[str, Any] = field(default_factory=dict)
    requirements_met: bool = field(default=False)
    
    def is_ready(self) -> bool:
        """Check if the activation context meets all requirements."""
        return self.requirements_met and self.readiness_level >= 1.0
        
    @classmethod
    def create(
        cls,
        context_id: str,
        readiness_level: float = 1.0,
        activation_environment: dict[str, Any] | None = None,
        requirements_met: bool = False,
    ) -> ActivationContext:
        return cls(
            context_id=context_id,
            readiness_level=readiness_level,
            activation_environment=activation_environment or {},
            requirements_met=requirements_met,
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ActivationContext",
            "context_id": self.context_id,
            "readiness_level": self.readiness_level,
            "activation_environment": self.activation_environment,
            "requirements_met": self.requirements_met,
        }


# =============================================================================
# ACTIVATION REQUIREMENT
# =============================================================================

@dataclass(frozen=True)
class ActivationRequirement:
    """
    Conditions that must be satisfied for orientation activation.
    
    SEMANTIC ROLE:
        - Represents semantic requirements for activation
        - Never represents runtime enforcement
        
    CHARACTERISTICS:
        - Immutable: Frozen dataclass
        - Semantic: Describes conditions, not execution
        - Deterministic: Requirements can be validated statically
        
    OWNERSHIP:
        - Owns: Requirement definitions and validation rules
        - Never owns: Enforcement engines, schedulers
    """
    
    requirement_id: str
    requirement_type: str  # e.g., "resource", "context", "dependency"
    required_value: Any = field(default=None)
    current_value: Any = field(default=None)
    satisfied: bool = field(default=False)
    
    @classmethod
    def create(
        cls,
        requirement_id: str,
        requirement_type: str,
        required_value: Any = None,
        current_value: Any = None,
        satisfied: bool = False,
    ) -> ActivationRequirement:
        return cls(
            requirement_id=requirement_id,
            requirement_type=requirement_type,
            required_value=required_value,
            current_value=current_value,
            satisfied=satisfied,
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ActivationRequirement",
            "requirement_id": self.requirement_id,
            "requirement_type": self.requirement_type,
            "required_value": self.required_value,
            "current_value": self.current_value,
            "satisfied": self.satisfied,
        }


# =============================================================================
# ACTIVATION RELATIONSHIP
# =============================================================================

@dataclass(frozen=True)
class ActivationRelationship:
    """
    Dependencies between orientations and activators.
    
    SEMANTIC ROLE:
        - Represents semantic activation dependencies
        - Never represents runtime relationships
        
    CHARACTERISTICS:
        - Immutable: Frozen dataclass
        - Semantic: Describes relationships, not execution
        - Deterministic: Relationships are static definitions
        
    OWNERSHIP:
        - Owns: Relationship definitions and semantics
        - Never owns: Runtime dependency trackers
    """
    
    relationship_id: str
    source_orientation: str  # Orientation identity
    target_orientation: str = field(default="")  # Dependency orientation identity
    relationship_type: str = field(default="activation")  # e.g., "activation", "prerequisite", "context"
    strength: float = field(default=1.0)  # 0.0 to 1.0
    active: bool = field(default=False)
    
    @classmethod
    def create(
        cls,
        relationship_id: str,
        source_orientation: str,
        target_orientation: str = "",
        relationship_type: str = "activation",
        strength: float = 1.0,
        active: bool = False,
    ) -> ActivationRelationship:
        return cls(
            relationship_id=relationship_id,
            source_orientation=source_orientation,
            target_orientation=target_orientation,
            relationship_type=relationship_type,
            strength=strength,
            active=active,
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ActivationRelationship",
            "relationship_id": self.relationship_id,
            "source_orientation": self.source_orientation,
            "target_orientation": self.target_orientation,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "active": self.active,
        }


# =============================================================================
# ACTIVATION PROJECTION
# =============================================================================

@dataclass(frozen=True)
class ActivationProjection:
    """
    Expected state after orientation activation.
    
    SEMANTIC ROLE:
        - Represents semantic prediction of post-activation state
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Immutable: Frozen dataclass
        - Semantic: Describes expected state, not behavior
        - Deterministic: Projections are static definitions
        
    OWNERSHIP:
        - Owns: Projection definitions and expected outcomes
        - Never owns: Runtime prediction engines
    """
    
    projection_id: str
    projected_state: str  # e.g., "Active", "Engaged"
    confidence: float = field(default=0.5)  # 0.0 to 1.0
    expected_context: dict[str, Any] = field(default_factory=dict)
    projected_at: str = field(default="")
    
    @classmethod
    def create(
        cls,
        projection_id: str,
        projected_state: str,
        confidence: float = 0.5,
        expected_context: dict[str, Any] | None = None,
        projected_at: str = "",
    ) -> ActivationProjection:
        return cls(
            projection_id=projection_id,
            projected_state=projected_state,
            confidence=confidence,
            expected_context=expected_context or {},
            projected_at=projected_at,
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ActivationProjection",
            "projection_id": self.projection_id,
            "projected_state": self.projected_state,
            "confidence": self.confidence,
            "expected_context": self.expected_context,
            "projected_at": self.projected_at,
        }


# =============================================================================
# ACTIVATION REFERENCE
# =============================================================================

@dataclass(frozen=True)
class ActivationReference:
    """
    How orientations reference their activation source.
    
    SEMANTIC ROLE:
        - Represents semantic activation provenance tracking
        - Never represents runtime references
        
    CHARACTERISTICS:
        - Immutable: Frozen dataclass
        - Semantic: Describes provenance, not execution
        - Deterministic: References are static definitions
        
    OWNERSHIP:
        - Owns: Reference definitions and provenance tracking
        - Never owns: Runtime reference managers
    """
    
    reference_id: str
    activated_by: str  # Identity of the activator
    activation_method: str = field(default="")  # e.g., "explicit", "implicit", "inferred"
    referenced_at: str = field(default="")
    context: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        reference_id: str,
        activated_by: str,
        activation_method: str = "",
        referenced_at: str = "",
        context: dict[str, Any] | None = None,
    ) -> ActivationReference:
        return cls(
            reference_id=reference_id,
            activated_by=activated_by,
            activation_method=activation_method,
            referenced_at=referenced_at or "",
            context=context or {},
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ActivationReference",
            "reference_id": self.reference_id,
            "activated_by": self.activated_by,
            "activation_method": self.activation_method,
            "referenced_at": self.referenced_at,
            "context": self.context,
        }


__all__ = [
    "ActivationContext",
    "ActivationRequirement",
    "ActivationRelationship",
    "ActivationProjection",
    "ActivationReference",
]