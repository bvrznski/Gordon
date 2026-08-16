# Salience Network Responsibility Model
# =====================================

"""
Responsibility model for the Salience Network.

This module defines the canonical responsibility contracts that establish
what this subsystem is responsible for and what it explicitly does NOT handle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Tuple


# =============================================================================
# RESPONSIBILITY CONTRACTS (Phase 4.8.1)
# =============================================================================

@dataclass(frozen=True)
class SalienceResponsibilityReference:
    """
    Reference artifact for Salience Network responsibility contracts.
    
    Provides external references to canonical responsibility definitions
    without runtime dependencies.
    """
    
    reference_id: str = field(default="")
    """Unique identifier for this reference."""
    
    target_type: str = field(default="responsibility")
    """Type of the target responsibility component."""
    
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
class SalienceResponsibilityRelationship:
    """
    Relationship artifact for responsibility contracts.
    
    Defines semantic relationships between responsibility artifacts
    without runtime behavior or scheduling.
    """
    
    source: str = field(default="")
    """Source of the relationship."""
    
    target: str = field(default="")
    """Target of the relationship."""
    
    relation_type: str = field(default="responsibility_chain")
    """Type of relationship (responsibility_chain, delegation, semantic)."""
    
    direction: str = field(default="unidirectional")
    """Direction of the relationship (unidirectional/bidirectional)."""
    
    @property
    def is_semantic(self) -> bool:
        """
        Validate that this relationship is purely semantic.
        
        Relationship must not involve runtime behavior or scheduling.
        """
        return self.relation_type in ("responsibility_chain", "delegation", "semantic")


@dataclass(frozen=True)
class SalienceResponsibilityRequirement:
    """
    Requirement artifact for responsibility contracts.
    
    Defines what must be satisfied for proper responsibility
    fulfillment without runtime dependencies.
    """
    
    requirement_id: str = field(default="")
    """Unique identifier for this requirement."""
    
    requirement_type: str = field(default="responsibility")
    """Type of requirement (responsibility, constraint, invariant)."""
    
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
class SalienceResponsibilityAuthority:
    """
    Authority artifact for responsibility contracts.
    
    Defines the authoritative source of truth for responsibility
    definitions without runtime dependencies.
    """
    
    authority_id: str = field(default="salience_responsibility")
    """Unique identifier for this authority."""
    
    scope: Tuple[str, ...] = field(
        default=(
            "responsibility",
            "ownership",
            "context",
            "integration",
        )
    )
    """Scope of authority over responsibility components."""
    
    @property
    def canonical_scope(self) -> FrozenSet[str]:
        """
        Return the canonical scope as an immutable set.
        """
        return frozenset(self.scope)


@dataclass(frozen=True)
class SalienceResponsibilityOwner:
    """
    Owner artifact for responsibility contracts.
    
    Establishes the canonical owner of each responsibility component
    without runtime dependencies or mutable state.
    """
    
    owner_id: str = field(default="Salience Network")
    """Unique identifier for this owner."""
    
    owned_components: Tuple[str, ...] = field(
        default=(
            "responsibility",
            "ownership",
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
class SalienceResponsibilityProjection:
    """
    Projection artifact for responsibility contracts.
    
    Defines how responsibility concepts project into semantic and
    evaluation domains without runtime execution.
    """
    
    projection_id: str = field(default="")
    """Unique identifier for this projection."""
    
    source_domain: str = field(default="responsibility")
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
# RESPONSIBILITY MODEL CONSTANTS (Phase 4.8.1)
# =============================================================================

RESPONSIBILITY_CONTRACT: SalienceResponsibilityOwner = SalienceResponsibilityOwner()
"""Canonical responsibility contract for the Salience Network."""

RESPONSIBILITY_AUTHORITY: SalienceResponsibilityAuthority = SalienceResponsibilityAuthority()
"""Canonical responsibility authority instance."""

DEFAULT_RESPONSIBILITY_PROJECTION: SalienceResponsibilityProjection = SalienceResponsibilityProjection(
    projection_id="default",
    source_domain="responsibility",
    target_domain="semantics"
)
"""Default responsibility projection instance."""