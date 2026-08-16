# Oriented Network Meta-Context (Immutable)
# ==========================================

"""
Meta-context specifications for the Orientation Meta-Model.

These contexts provide contextual organization without owning mutable state.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchitectureContext:
    """
    Architectural context for the Orientation Meta-Model.
    
    Provides architectural organizational context.
    """
    pass


@dataclass(frozen=True)
class SemanticContext:
    """
    Semantic context for the Orientation Meta-Model.
    
    Provides semantic organizational context.
    """
    pass


@dataclass(frozen=True)
class LifecycleContext:
    """
    Lifecycle context for the Orientation Meta-Model.
    
    Provides lifecycle-related contextual organization.
    """
    pass


@dataclass(frozen=True)
class GovernanceContext:
    """
    Governance context for the Orientation Meta-Model.
    
    Provides governance-related contextual organization.
    """
    pass


@dataclass(frozen=True)
class EvaluationContext:
    """
    Evaluation context for the Orientation Meta-Model.
    
    Provides evaluation-related contextual organization.
    """
    pass


@dataclass(frozen=True)
class PersistenceContext:
    """
    Persistence context for the Orientation Meta-Model.
    
    Provides persistence-related contextual organization.
    """
    pass


@dataclass(frozen=True)
class IntegrationContext:
    """
    Integration context for the Orientation Meta-Model.
    
    Provides integration-related contextual organization.
    """
    pass


@dataclass(frozen=True)
class RepositoryContext:
    """
    Repository context for the Orientation Meta-Model.
    
    Provides repository-wide contextual organization.
    """
    pass