# Multi-Domain Reward Engine - Classifiers Package (Phase 4.10.5)
# ================================================================

"""
Classifier package for Phase 4.10.5 Multi-Domain Reward Engine.

This package contains domain-specific classifiers that transform reward estimates
into classified reward domains. Each classifier owns exactly one semantic domain.
"""

from __future__ import annotations

# Base classes
from .base import (
    BaseRewardClassifier,
    ClassifierResult,
)

__all__ = [
    # Base classes
    "BaseRewardClassifier",
    "ClassifierResult",
]