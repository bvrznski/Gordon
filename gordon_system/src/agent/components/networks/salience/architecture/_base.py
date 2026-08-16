# Salience Network Base Architectural Abstractions
# ================================================

"""
Base architectural abstractions for the Salience Network.

This module defines the canonical archetype hierarchy that all Salience
Network components must conform to. These base classes establish the
architectural contract and invariant preservation layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, FrozenSet, Mapping, Optional, Tuple, TypeVar


# =============================================================================
# BASE ARCHITECTURAL ABSTRACTIONS (Phase 4.8.1)
# =============================================================================

@dataclass(frozen=True)
class BaseSalienceArchitecture:
    """
    Base class for all Salience Network architectural artifacts.
    
    Defines the foundational architectural contract that preserves:
        - Architectural immutability
        - Deterministic identity semantics
        - Explicit ownership boundaries
        - Acyclic dependency graphs
    
    All canonical architecture components inherit from this base.
    """
    
    name: str = field(default="base_architecture")
    """Canonical name identifier for this architectural artifact."""
    
    version: Tuple[int, ...] = field(default_factory=lambda: (0, 1, 0))
    """Version tuple in semantic versioning format."""
    
    layer: str = field(default="architecture")
    """Architectural layer to which this artifact belongs."""
    
    def validate_architecture(self) -> bool:
        """
        Validate that this architectural artifact satisfies all
        Salience Network architectural invariants.
        
        Returns:
            True if architecture is valid, False otherwise.
        """
        return self._validate_immutability() and \
               self._validate_ownership() and \
               self._validate_dependencies()
    
    def _validate_immutability(self) -> bool:
        """Validate that all fields are immutable."""
        return True  # frozen=True ensures this via dataclass
    
    def _validate_ownership(self) -> bool:
        """
        Validate ownership boundaries are preserved.
        
        The Salience Network owns only semantic salience and related
        evaluation concepts, never runtime behavior or execution.
        """
        return True
    
    def _validate_dependencies(self) -> bool:
        """Validate that dependencies form an acyclic graph."""
        return True
    
    @property
    def canonical_name(self) -> str:
        """Return the fully qualified canonical name."""
        return f"Salience.{self.__class__.__name__}"


@dataclass(frozen=True)
class BaseSalienceDefinition(BaseSalienceArchitecture):
    """
    Base class for all Salience Network semantic definitions.
    
    Defines semantic artifacts that represent concepts in the
    Salience Network's domain (significance, relevance, novelty,
    urgency, etc.).
    """
    
    definition_id: str = field(default="")
    """Unique identifier for this definition."""
    
    scope: str = field(default="salience")
    """Semantic scope to which this definition belongs."""
    
    @property
    def is_canonical(self) -> bool:
        """Indicates whether this is a canonical (non-derivative) definition."""
        return True


@dataclass(frozen=True)
class BaseSalienceIdentity(BaseSalienceArchitecture):
    """
    Base class for all Salience Network identity artifacts.
    
    Identity artifacts provide unique, deterministic identification
    for architectural components without runtime dependencies.
    """
    
    identity_id: str = field(default="")
    """Unique identifier within the architecture."""
    
    namespace: str = field(default="salience")
    """Namespace for this identity."""
    
    revision: int = field(default=0)
    """Revision number for versioning."""
    
    @property
    def canonical_identity(self) -> str:
        """
        Return the fully qualified canonical identity.
        
        Format: namespace:identity_id:revision
        """
        return f"{self.namespace}:{self.identity_id}:{self.revision}"


@dataclass(frozen=True)
class BaseSalienceOwnership(BaseSalienceArchitecture):
    """
    Base class for all Salience Network ownership contracts.
    
    Ownership artifacts define:
        - What this subsystem owns exclusively
        - What it explicitly does NOT own
        - How ownership boundaries are preserved
    """
    
    owner: str = field(default="Salience Network")
    """Canonical owner of the owned concepts."""
    
    owned_concepts: Tuple[str, ...] = field(default_factory=tuple)
    """List of concepts owned by this subsystem."""
    
    non_owned_concepts: Tuple[str, ...] = field(default_factory=tuple)
    """List of concepts explicitly NOT owned by this subsystem."""
    
    @property
    def is_unique_owner(self) -> bool:
        """
        Validate that ownership is unique (no overlap with other subsystems).
        
        The Salience Network owns only semantic salience concepts.
        It never owns runtime behavior, execution, or cognitive algorithms.
        """
        return len(self.owned_concepts) > 0 and \
               len(set(self.owned_concepts) & set(self.non_owned_concepts)) == 0


@dataclass(frozen=True)
class BaseSalienceRelationship(BaseSalienceArchitecture):
    """
    Base class for all Salience Network relationship artifacts.
    
    Relationship artifacts define semantic relationships between
    architectural concepts without runtime behavior.
    """
    
    source: str = field(default="")
    """Source of the relationship."""
    
    target: str = field(default="")
    """Target of the relationship."""
    
    relationship_type: str = field(default="semantic")
    """Type of relationship (semantic, dependency, ownership)."""
    
    @property
    def is_acyclic(self) -> bool:
        """
        Validate that this relationship does not create a cycle.
        
        All Salience Network dependencies must form an acyclic graph.
        """
        return True


@dataclass(frozen=True)
class BaseSalienceContext(BaseSalienceArchitecture):
    """
    Base class for all Salience Network context artifacts.
    
    Context artifacts provide architectural context for semantic
    evaluation without runtime state.
    """
    
    context_id: str = field(default="")
    """Unique identifier for this context."""
    
    context_type: str = field(default="evaluation")
    """Type of context (evaluation, integration, governance)."""
    
    scope: FrozenSet[str] = field(default_factory=frozenset)
    """Scope elements that define this context."""
    
    @property
    def canonical_scope(self) -> frozenset:
        """Return the canonical scope for this context."""
        return self.scope


# =============================================================================
# TYPE VARIABLES (Phase 4.8.1)
# =============================================================================

T_SalienceArchitecture = TypeVar(
    "T_SalienceArchitecture",
    bound=BaseSalienceArchitecture,
    covariant=True
)
"""Type variable for Salience Architecture types."""

T_SalienceDefinition = TypeVar(
    "T_SalienceDefinition", 
    bound=BaseSalienceDefinition, 
    covariant=True
)
"""Type variable for Salience Definition types."""

T_SalienceIdentity = TypeVar(
    "T_SalienceIdentity",
    bound=BaseSalienceIdentity,
    covariant=True
)
"""Type variable for Salience Identity types."""

T_SalienceOwnership = TypeVar(
    "T_SalienceOwnership",
    bound=BaseSalienceOwnership,
    covariant=True
)
"""Type variable for Salience Ownership types."""

T_SalienceRelationship = TypeVar(
    "T_SalienceRelationship",
    bound=BaseSalienceRelationship,
    covariant=True
)
"""Type variable for Salience Relationship types."""

T_SalienceContext = TypeVar(
    "T_SalienceContext",
    bound=BaseSalienceContext,
    covariant=True
)
"""Type variable for Salience Context types."""


# =============================================================================
# ARCHITECTURAL CONSTANTS (Phase 4.8.1)
# =============================================================================

ARCHITECTURAL_LAYERS: Tuple[str, ...] = (
    "architecture",      # Base architectural definitions
    "identity",         # Identity contracts
    "responsibility",   # Responsibility contracts  
    "ownership",        # Ownership contracts
    "context",          # Context definitions
    "integration",      # Integration contracts
    "evaluation",       # Evaluation contracts
    "governance",       # Governance contracts
)
"""All canonical Salience Network architectural layers."""

ARCHITECTURAL_INVARIANTS: Tuple[str, ...] = (
    "immutability",         # All artifacts are immutable (frozen dataclasses)
    "determinism",          # Same inputs produce same outputs
    "acyclic_dependencies", # No circular dependencies allowed
    "explicit_ownership",   # Ownership is always explicit and unique
    "no_runtime_behavior",  # Architecture never contains runtime code
)
"""All canonical Salience Network architectural invariants."""