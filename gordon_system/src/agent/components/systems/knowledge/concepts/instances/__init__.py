# Knowledge Concepts - Instances - Phase 6.3
# ===========================================

"""
Instance Management for Gordon's Concept Subsystem.

Instances are concrete realizations of concepts in the world. This module
provides utilities for instance classification, property assignment, and
instance lifecycle management.
"""

from __future__ import annotations

from ..shared.contract import (
    ConceptInstance,
    ConceptClassification,
    ClassificationKind,
)

# Import manager and classifier classes when they're implemented
# from .manager import InstanceManager
# from .classifier import InstanceClassifier

__all__ = [
    # Core types
    "ConceptInstance",
    "ConceptClassification",
    "ClassificationKind",
]