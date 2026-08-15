# Identity Continuity Assessment Model
# =====================================

"""
Immutable identity continuity assessment model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityContinuityAssessment:
    """
    Immutable representation of an identity continuity assessment.
    
    PROPERTIES:
        • kind: What aspect is being assessed (IdentityContinuityAssessmentKind.*)
        • classification: Continuity status classification
        • stable_aspects: Aspects that remain stable
        • changed_aspects: Aspects that have changed
        • revision_lineage: Revision history links
        • known_discontinuities: Known breaks in continuity
        • confidence: Confidence in assessment (0.0 to 1.0)
    """
    
    kind: str = ""
    """What aspect is being assessed (IdentityContinuityAssessmentKind.*)."""
    
    classification: str = "continuous"
    """Continuity status classification:
       - continuous: Stable identity with revisioned changes
       - mostly_continuous: Mostly stable, some gaps
       - partially_continu ous: Significant discontinuities
       - discontinuous: Major breaks in identity
       - insufficient_evidence: Not enough information
       - unknown: Cannot determine
    """
    
    stable_aspects: Tuple[str, ...] = field(default_factory=tuple)
    """Identity aspect IDs that remain stable."""
    
    changed_aspects: Tuple[str, ...] = field(default_factory=tuple)
    """Identity aspect IDs that have changed."""
    
    revision_lineage: Tuple[str, ...] = field(default_factory=tuple)
    """Revision IDs in the lineage chain."""
    
    known_discontinuities: Tuple[str, ...] = field(default_factory=tuple)
    """Known breaks or gaps in continuity."""
    
    confidence: float = 1.0
    """Confidence in this assessment (0.0 to 1.0)."""