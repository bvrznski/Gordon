# Oriented Network Architectural Views (Descriptions)
# ===================================================

"""
Architectural descriptions of the Orientation Meta-Model.

These are descriptions, not separate models. They provide different
perspectives on the single canonical meta-model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StructuralView:
    """
    Structural description of the Orientation Meta-Model.
    
    Describes the structural composition of the architecture without
    defining new semantic concepts.
    """
    pass


@dataclass(frozen=True)
class BehavioralPreparationView:
    """
    Behavioral preparation description for the Orientation Meta-Model.
    
    Describes how runtime behavior is prepared from the canonical
    meta-model without implementing behavior directly.
    """
    pass


@dataclass(frozen=True)
class LifecycleArchitecturalView:
    """
    Lifecycle architectural description.
    
    Describes lifecycle aspects of the architecture as a description,
    not an implementation.
    """
    pass


@dataclass(frozen=True)
class EvaluationArchitecturalView:
    """
    Evaluation architectural description.
    
    Describes evaluation aspects of the architecture as a description,
    not an implementation.
    """
    pass


@dataclass(frozen=True)
class IntegrationArchitecturalView:
    """
    Integration architectural description.
    
    Describes integration aspects of the architecture as a description,
    not an implementation.
    """
    pass