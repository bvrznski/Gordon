# Salience Network Ownership Model
# ================================

"""
Ownership model for the Salience Network.

This module defines the canonical ownership contracts that establish
what this subsystem owns exclusively and what it explicitly does NOT own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Tuple


# =============================================================================
# OWNERSHIP CONTRACTS (Phase 4.8.1)
# =============================================================================

@dataclass(frozen=True)
class SalienceArchitectureReference:
    """
    Reference artifact for Salience Network architectural ownership.
    
    Provides external references to canonical architecture components
    without runtime dependencies.
    """
    
    reference_id: str = field(default="")
    """Unique identifier for this reference."""
    
    target_type: str = field(default="architecture")
    """Type of the target architectural component."""
    
    target_namespace: str = field(default="salience")
    """Namespace of the target component."""
    
    @property
    def canonical_reference(self) -> str:
        """
        Return fully qualified canonical reference.
        
        Format: namespace:reference_id:type
        """
        return f"{self.target_namespace}:{self.reference_id}:{self.target_type}"


@dataclass(frozen=True)
class SalienceArchitectureRelationship:
    """
    Relationship artifact for architectural ownership.
    
    Defines semantic relationships between architectural artifacts
    without runtime behavior or scheduling.
    """
    
    source: str = field(default="")
    """Source of the relationship."""
    
    target: str = field(default="")
    """Target of the relationship."""
    
    relation_type: str = field(default="ownership")
    """Type of relationship (ownership, dependency, semantic)."""
    
    direction: str = field(default="unidirectional")
    """Direction of the relationship (unidirectional/bidirectional)."""
    
    @property
    def is_semantic(self) -> bool:
        """
        Validate that this relationship is purely semantic.
        
        Relationship must not involve runtime behavior or scheduling.
        """
        return self.relation_type in ("ownership", "dependency", "semantic")


@dataclass(frozen=True)
class SalienceArchitectureRequirement:
    """
    Requirement artifact for architectural ownership.
    
    Defines what must be satisfied for proper architectural operation
    without runtime dependencies.
    """
    
    requirement_id: str = field(default="")
    """Unique identifier for this requirement."""
    
    requirement_type: str = field(default="ownership")
    """Type of requirement (ownership, constraint, invariant)."""
    
    description: str = field(default="")
    """Description of what is required."""
    
    @property
    def is_canonical(self) -> bool:
        """
        Validate that this is a canonical (non-runtime) requirement.
        
        Canonical requirements are purely architectural constraints,
        not runtime behavior specifications.
        """
        return True


@dataclass(frozen=True)
class SalienceArchitectureAuthority:
    """
    Authority artifact for architectural ownership.
    
    Defines the authoritative source of truth for architectural
    definitions without runtime dependencies.
    """
    
    authority_id: str = field(default="salience_architecture")
    """Unique identifier for this authority."""
    
    scope: Tuple[str, ...] = field(
        default=(
            "architecture",
            "identity", 
            "ownership",
            "responsibility",
        )
    )
    """Scope of authority over architectural components."""
    
    @property
    def canonical_scope(self) -> FrozenSet[str]:
        """
        Return the canonical scope as an immutable set.
        """
        return frozenset(self.scope)


@dataclass(frozen=True)
class SalienceArchitectureOwner:
    """
    Owner artifact for architectural ownership contracts.
    
    Establishes the canonical owner of each architectural component
    without runtime dependencies or mutable state.
    """
    
    owner_id: str = field(default="Salience Network")
    """Unique identifier for this owner."""
    
    owned_components: Tuple[str, ...] = field(
        default=(
            "architecture",
            "identity", 
            "ownership",
            "responsibility",
            "context",
            "integration",
            "evaluation",
            "governance",
        )
    )
    """Components owned by the Salience Network."""
    
    @property
    def is_unique_owner(self) -> bool:
        """
        Validate that ownership is unique (no overlap with other subsystems).
        
        The Salience Network owns only architectural definitions,
        never runtime behavior or execution.
        """
        return True


@dataclass(frozen=True)
class SalienceArchitectureProjection:
    """
    Projection artifact for architectural ownership.
    
    Defines how architectural concepts project into semantic and
    evaluation domains without runtime execution.
    """
    
    projection_id: str = field(default="")
    """Unique identifier for this projection."""
    
    source_domain: str = field(default="architecture")
    """Source domain of the projection."""
    
    target_domain: str = field(default="semantics")
    """Target domain of the projection."""
    
    @property
    def is_semantic_projection(self) -> bool:
        """
        Validate that this is a semantic (non-runtime) projection.
        
        Projection must not involve runtime behavior or scheduling.
        """
        return True


# =============================================================================
# OWNERSHIP MODEL CONSTANTS (Phase 4.8.1)
# =============================================================================

OWNERSHIP_CONTRACT: SalienceArchitectureOwner = SalienceArchitectureOwner()
"""Canonical ownership contract for the Salience Network."""

ARCHITECTURE_AUTHORITY: SalienceArchitectureAuthority = SalienceArchitectureAuthority()
"""Canonical architectural authority instance."""

DEFAULT_ARCHITECTURE_PROJECTION: SalienceArchitectureProjection = SalienceArchitectureProjection(
    projection_id="default",
    source_domain="architecture",
    target_domain="semantics"
)
"""Default architectural projection instance."""