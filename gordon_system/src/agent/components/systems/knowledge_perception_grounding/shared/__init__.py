# Knowledge-Perception Grounding - Shared Contracts Package
# ==========================================================

"""
Shared contract definitions for the Knowledge-Perception Grounding layer.

This package provides canonical contracts for:
- Observations and their sources
- Percepts, groups, and embeddings
- Correspondence between percepts and concepts
- Novelty detection
- Grounding records
- Semantic candidates
- Active perception requests
- Reality validation

All contracts follow the Phase 5.6 specification and preserve
provenance, confidence, uncertainty, and determinism.
"""

from __future__ import annotations

# Core modules
from .observation import (
    Observation,
    ObservationSession,
    ObservationSource,
)

from .percept import (
    Percept,
    PerceptGroup,
    PerceptEmbedding,
    PerceptClassification,
    PerceptRepresentation,
)

__all__ = [
    # Observation
    "Observation",
    "ObservationSession",
    "ObservationSource",
    
    # Percept
    "Percept",
    "PerceptGroup",
    "PerceptEmbedding",
    "PerceptClassification",
    "PerceptRepresentation",
]