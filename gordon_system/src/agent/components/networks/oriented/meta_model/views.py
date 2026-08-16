# Oriented Network Semantic Views (Projections)
# ==============================================

"""
Semantic views as projections of one canonical Orientation Meta-Model.

All views are projections - they reference the canonical meta-model but
do not contain independent semantic definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OntologyView:
    """
    Ontological perspective on the Orientation Meta-Model.
    
    This view provides ontological specifications derived from
    the canonical meta-model.
    """
    pass


@dataclass(frozen=True)
class ContentView:
    """
    Content perspective on the Orientation Meta-Model.
    
    This view provides content-related specifications derived from
    the canonical meta-model.
    """
    pass


@dataclass(frozen=True)
class StateView:
    """
    State perspective on the Orientation Meta-Model.
    
    This view provides state-related specifications derived from
    the canonical meta-model.
    """
    pass


@dataclass(frozen=True)
class LifecycleView:
    """
    Lifecycle perspective on the Orientation Meta-Model.
    
    This view provides lifecycle-related specifications derived from
    the canonical meta-model.
    """
    pass


@dataclass(frozen=True)
class PersistenceView:
    """
    Persistence perspective on the Orientation Meta-Model.
    
    This view provides persistence-related specifications derived from
    the canonical meta-model.
    """
    pass


@dataclass(frozen=True)
class EvaluationView:
    """
    Evaluation perspective on the Orientation Meta-Model.
    
    This view provides evaluation-related specifications derived from
    the canonical meta-model.
    """
    pass


@dataclass(frozen=True)
class GovernanceView:
    """
    Governance perspective on the Orientation Meta-Model.
    
    This view provides governance-related specifications derived from
    the canonical meta-model.
    """
    pass


@dataclass(frozen=True)
class IntegrationView:
    """
    Integration perspective on the Orientation Meta-Model.
    
    This view provides integration-related specifications derived from
    the canonical meta-model.
    """
    pass