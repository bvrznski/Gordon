# Abduction Evidence Module - Phase 7.3
# =====================================

"""
Evidence management for abductive reasoning.

This module provides:
    - Evidence artifact definitions
    - Evidence set construction and manipulation
    - Source reliability tracking
    - Quality constraints
"""

from agent.components.systems.cognition.reasoning.abductive.evidence.artifact import (
    AbductionEvidence,
    EvidenceSource,
    EvidenceKind,
    EvidenceArtifact,
)

from agent.components.systems.cognition.reasoning.abductive.evidence.set import (
    EvidenceSet,
    EvidenceSetIdentity,
    MissingEvidence,
    EvidenceQuality,
)

__all__ = [
    "AbductionEvidence",
    "EvidenceSource", 
    "EvidenceKind",
    "EvidenceArtifact",
    "EvidenceSet",
    "EvidenceSetIdentity",
    "MissingEvidence",
    "EvidenceQuality",
]