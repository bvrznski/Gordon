# Salience Network Context Model
# ==============================

"""
Context model for the Salience Network.

This module defines the canonical context artifacts that provide
architectural context for semantic evaluation without runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Tuple


# =============================================================================
# CONTEXT ARTIFACTS (Phase 4.8.1)
# =============================================================================

@dataclass(frozen=True)
class SalienceContextReference:
    """
    Reference artifact for Salience Network context definitions.
    
    Provides external references to canonical context artifacts
    without runtime dependencies.
    """
    
    reference_id: str = field(default="")
    """Unique identifier for this reference."""
    
    target_type: str = field(default="context")
    """Type of the target context component."""
    
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
class SalienceContextRelationship:
    """
    Relationship artifact for context definitions.
    
    Defines semantic relationships between context artifacts
    without runtime behavior or scheduling.
    """
    
    source: str = field(default="")
    """Source of the relationship."""
    
    target: str = field(default="")
    """Target of the relationship."""
    
    relation_type: str = field(default="contextual")
    """Type of relationship (contextual, dependency, semantic)."""
    
    direction: str = field(default="unidirectional")
    """Direction of the relationship (unidirectional/bidirectional)."""
    
    @property
    def is_semantic(self) -> bool:
        """
        Validate that this relationship is purely semantic.
        
        Relationship must not involve runtime behavior or scheduling.
        """
        return self.relation_type in ("contextual", "dependency", "semantic")


@dataclass(frozen=True)
class SalienceContextRequirement:
    """
    Requirement artifact for context definitions.
    
    Defines what must be satisfied for proper context operation
    without runtime dependencies.
    """
    
    requirement_id: str = field(default="")
    """Unique identifier for this requirement."""
    
    requirement_type: str = field(default="context")
    """Type of requirement (context, constraint, invariant)."""
    
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
class SalienceContextAuthority:
    """
    Authority artifact for context definitions.
    
    Defines the authoritative source of truth for context
    definitions without runtime dependencies.
    """
    
    authority_id: str = field(default="salience_context")
    """Unique identifier for this authority."""
    
    scope: Tuple[str, ...] = field(
        default=(
            "context",
            "integration",
            "evaluation",
            "governance",
        )
    )
    """Scope of authority over context components."""
    
    @property
    def canonical_scope(self) -> FrozenSet[str]:
        """
        Return the canonical scope as an immutable set.
        """
        return frozenset(self.scope)


@dataclass(frozen=True)
class SalienceContextOwner:
    """
    Owner artifact for context definitions.
    
    Establishes the canonical owner of each context component
    without runtime dependencies or mutable state.
    """
    
    owner_id: str = field(default="Salience Network")
    """Unique identifier for this owner."""
    
    owned_components: Tuple[str, ...] = field(
        default=(
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
class SalienceContextProjection:
    """
    Projection artifact for context definitions.
    
    Defines how context concepts project into semantic and
    evaluation domains without runtime execution.
    """
    
    projection_id: str = field(default="")
    """Unique identifier for this projection."""
    
    source_domain: str = field(default="context")
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
# CONTEXT MODEL CONSTANTS (Phase 4.8.1)
# =============================================================================

CONTEXT_CONTRACT: SalienceContextOwner = SalienceContextOwner()
"""Canonical context contract for the Salience Network."""

CONTEXT_AUTHORITY: SalienceContextAuthority = SalienceContextAuthority()
"""Canonical context authority instance."""

DEFAULT_CONTEXT_PROJECTION: SalienceContextProjection = SalienceContextProjection(
    projection_id="default",
    source_domain="context",
    target_domain="semantics"
)
"""Default context projection instance."""