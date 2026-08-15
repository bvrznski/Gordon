# Composition Module for Internal Context
# =======================================

"""
Composition models for internal context assembly.

These modules handle the composition of context from individual projections:
    • Completeness: Structured completeness assessment
    • Confidence: Structured confidence assessment  
    • Freshness: Structured freshness assessment
    • Conflicts: Conflict detection and recording
    • Normalization: Deterministic normalization of values
    • Prioritization: Selection when capacity is exceeded
"""

from __future__ import annotations

# Composition models (defined in separate files)
from .completeness import InternalContextCompleteness
from .confidence import InternalContextConfidence
from .freshness import InternalContextFreshness
from .conflicts import InternalContextConflict, ContextConflictId

__all__ = [
    "InternalContextCompleteness",
    "InternalContextConfidence",
    "InternalContextFreshness",
    "InternalContextConflict",
    "ContextConflictId",
]