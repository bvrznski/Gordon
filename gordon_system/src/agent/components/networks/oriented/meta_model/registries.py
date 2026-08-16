# Oriented Network Registries (Declarative)
# ===========================================

"""
Canonical registries for the Orientation Meta-Model.

These registries provide declarative model discovery and classification
without runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OntologyRegistry:
    """
    Canonical ontology registry.
    
    Provides ontology model discovery and semantic classification.
    """
    pass


@dataclass(frozen=True)
class StateRegistry:
    """
    Canonical state registry.
    
    Provides state model discovery and semantic classification.
    """
    pass


@dataclass(frozen=True)
class ContentRegistry:
    """
    Canonical content registry.
    
    Provides content model discovery and semantic classification.
    """
    pass


@dataclass(frozen=True)
class LifecycleRegistry:
    """
    Canonical lifecycle registry.
    
    Provides lifecycle model discovery and semantic classification.
    """
    pass


@dataclass(frozen=True)
class PersistenceRegistry:
    """
    Canonical persistence registry.
    
    Provides persistence model discovery and semantic classification.
    """
    pass


@dataclass(frozen=True)
class EvaluationRegistry:
    """
    Canonical evaluation registry.
    
    Provides evaluation model discovery and semantic classification.
    """
    pass


@dataclass(frozen=True)
class GovernanceRegistry:
    """
    Canonical governance registry.
    
    Provides governance model discovery and semantic classification.
    """
    pass


@dataclass(frozen=True)
class IntegrationRegistry:
    """
    Canonical integration registry.
    
    Provides integration model discovery and semantic classification.
    """
    pass