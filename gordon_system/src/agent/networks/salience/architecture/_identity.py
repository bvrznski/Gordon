# Salience Network Architectural Identity Definitions
# ===================================================

"""
Architectural identity definitions for the Salience Network.

This module defines the canonical identity artifacts that establish
the unique architectural role of the Salience Network within Gordon.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Tuple


# =============================================================================
# ARCHITECTURAL IDENTITY (Phase 4.8.1)
# =============================================================================

@dataclass(frozen=True)
class SalienceArchitecture:
    """
    Canonical architectural definition of the Salience Network.
    
    Defines the complete architectural identity including:
        - Layer structure and hierarchy
        - Dependency relationships
        - Ownership boundaries
        - Invariant guarantees
    
    CANONICAL HIERARCHY (Immutable):
        Architecture
            ↓ Identity
                ↓ Responsibility
                    ↓ Ownership
                        ↓ Context
                            ↓ Integration
                                ↓ Evaluation
                                    ↓ Governance
    """
    
    name: str = field(default="Salience Network")
    """Canonical architectural name."""
    
    version: Tuple[int, ...] = field(default_factory=lambda: (0, 1, 0))
    """Architectural version tuple."""
    
    layer: str = field(default="cognitive_network")
    """Architectural layer membership."""
    
    layers: Tuple[str, ...] = field(
        default=(
            "architecture",
            "identity", 
            "responsibility",
            "ownership",
            "context",
            "integration",
            "evaluation",
            "governance",
        )
    )
    """All canonical architectural layers."""
    
    dependency_graph: dict[str, FrozenSet[str]] = field(
        default_factory=lambda: {
            "architecture": frozenset(),
            "identity": frozenset({"architecture"}),
            "responsibility": frozenset({"identity"}),
            "ownership": frozenset({"responsibility"}),
            "context": frozenset({"ownership"}),
            "integration": frozenset({"context"}),
            "evaluation": frozenset({"integration"}),
            "governance": frozenset({"evaluation"}),
        }
    )
    """Architectural dependency graph (must be acyclic)."""
    
    @property
    def canonical_name(self) -> str:
        """Return fully qualified canonical name."""
        return f"Salience.{self.__class__.__name__}"
    
    def validate_acyclic(self) -> bool:
        """
        Validate that dependencies form an acyclic graph.
        
        Returns:
            True if no circular dependencies exist.
        """
        visited = set()
        rec_stack = set()
        
        for node in self.dependency_graph:
            if not self._dfs_validate(node, visited, rec_stack):
                return False
        return True
    
    def _dfs_validate(self, node: str, visited: set, rec_stack: set) -> bool:
        """Depth-first validation of acyclic dependency graph."""
        if node in rec_stack:
            return False
        if node in visited:
            return True
        
        visited.add(node)
        rec_stack.add(node)
        
        for dep in self.dependency_graph.get(node, frozenset()):
            if not self._dfs_validate(dep, visited, rec_stack):
                return False
        
        rec_stack.discard(node)
        return True


@dataclass(frozen=True)
class SalienceIdentity:
    """
    Identity artifact for the Salience Network.
    
    Provides unique identification and semantic context without
    runtime dependencies or mutable state.
    """
    
    identity_id: str = field(default="salience_network")
    """Unique identifier within architecture namespace."""
    
    namespace: str = field(default="gordon")
    """Architecture namespace."""
    
    revision: int = field(default=0)
    """Revision number for versioning."""
    
    display_name: str = field(default="Salience Network")
    """Human-readable display name."""
    
    description: str = field(
        default="Semantic salience estimation and evaluation subsystem"
    )
    """Canonical description of this identity's purpose."""
    
    @property
    def canonical_identity(self) -> str:
        """
        Return fully qualified canonical identity.
        
        Format: namespace:identity_id:revision
        """
        return f"{self.namespace}:{self.identity_id}:{self.revision}"
    
    @property
    def is_canonical(self) -> bool:
        """Indicates this is a canonical (non-derivative) identity."""
        return True


@dataclass(frozen=True)
class SalienceDefinition:
    """
    Semantic definition artifact for Salience Network concepts.
    
    Defines canonical semantic concepts including significance,
    relevance, novelty, urgency, and their relationships.
    """
    
    definition_id: str = field(default="")
    """Unique identifier for this definition."""
    
    scope: str = field(default="salience")
    """Semantic scope to which this definition belongs."""
    
    category: str = field(default="concept")
    """Definition category (concept, relationship, constraint)."""
    
    description: str = field(default="")
    """Canonical description of the semantic concept."""
    
    @property
    def canonical_name(self) -> str:
        """Return fully qualified canonical name."""
        return f"Salience.{self.__class__.__name__}.{self.definition_id}"


@dataclass(frozen=True)
class SalienceOwnership:
    """
    Ownership contract artifact for Salience Network.
    
    Defines what this subsystem owns exclusively and what it
    explicitly does NOT own, establishing clear boundaries.
    """
    
    owner: str = field(default="Salience Network")
    """Canonical owner of the owned concepts."""
    
    owned_concepts: Tuple[str, ...] = field(
        default=(
            "semantic salience",
            "significance estimation",
            "relevance representation",
            "novelty representation",
            "urgency representation",
            "salience ontology",
            "contextual importance",
            "conflict significance",
            "uncertainty significance",
            "prediction-error significance",
            "motivational significance",
        )
    )
    """Concepts owned exclusively by Salience Network."""
    
    non_owned_concepts: Tuple[str, ...] = field(
        default=(
            "attention allocation",
            "executive control", 
            "planning",
            "reasoning",
            "decision formation",
            "working memory",
            "runtime scheduling",
            "behavioral execution",
            "cognitive algorithms",
        )
    )
    """Concepts explicitly NOT owned by Salience Network."""
    
    @property
    def is_unique_owner(self) -> bool:
        """
        Validate that ownership is unique (no overlap with other subsystems).
        """
        return len(set(self.owned_concepts) & set(self.non_owned_concepts)) == 0


@dataclass(frozen=True)
class SalienceResponsibility:
    """
    Responsibility contract artifact for Salience Network.
    
    Defines what this subsystem is responsible for and what
    it explicitly does NOT handle.
    """
    
    responsibilities: Tuple[str, ...] = field(
        default=(
            "semantic salience evaluation",
            "significance estimation framework",
            "relevance representation contracts",
            "novelty representation contracts",
            "urgency representation contracts",
            "salience state management",
            "contextual importance assessment",
        )
    )
    """Responsibilities owned by Salience Network."""
    
    non_responsibilities: Tuple[str, ...] = field(
        default=(
            "runtime execution",
            "behavioral scheduling",
            "cognitive resource allocation",
            "executive decision making",
            "planning formulation",
            "reasoning execution",
        )
    )
    """Responsibilities explicitly NOT handled by Salience Network."""
    
    @property
    def is_consistent(self) -> bool:
        """
        Validate that responsibilities are consistent and non-overlapping.
        """
        return len(set(self.responsibilities) & set(self.non_responsibilities)) == 0


@dataclass(frozen=True)
class SalienceScope:
    """
    Scope artifact defining the semantic domain of Salience Network.
    
    Establishes boundaries for what is within and outside the
    semantic evaluation domain.
    """
    
    semantic_domain: FrozenSet[str] = field(
        default=frozenset((
            "significance",
            "relevance", 
            "novelty",
            "urgency",
            "contextual_importance",
            "conflict_significance",
            "uncertainty_significance",
            "prediction_error_significance",
            "motivational_significance",
        ))
    )
    """Semantic concepts within Salience Network domain."""
    
    external_domain: FrozenSet[str] = field(
        default=frozenset((
            "attention_allocation",
            "executive_control",
            "planning",
            "reasoning",
            "decision_formation",
            "working_memory",
            "runtime_execution",
        ))
    )
    """Semantic concepts outside Salience Network domain."""
    
    @property
    def is_bounded(self) -> bool:
        """
        Validate that scope has clear boundaries (no overlap).
        """
        return len(self.semantic_domain & self.external_domain) == 0


# =============================================================================
# ARCHITECTURAL IDENTITY CONSTANTS (Phase 4.8.1)
# =============================================================================

SALIENCE_ARCHITECTURE: SalienceArchitecture = SalienceArchitecture()
"""Canonical Salience Network architecture instance."""

SALIENCE_IDENTITY: SalienceIdentity = SalienceIdentity()
"""Canonical Salience Network identity instance."""

SALIENCE_OWNERSHIP: SalienceOwnership = SalienceOwnership()
"""Canonical Salience Network ownership contract instance."""

SALIENCE_RESPONSIBILITY: SalienceResponsibility = SalienceResponsibility()
"""Canonical Salience Network responsibility contract instance."""

SALIENCE_SCOPE: SalienceScope = SalienceScope()
"""Canonical Salience Network scope definition instance."""