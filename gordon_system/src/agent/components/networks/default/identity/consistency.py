# Identity Consistency Assessment Model
# =====================================

"""
Immutable identity consistency assessment model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityConsistencyAssessment:
    """
    Immutable representation of an identity consistency assessment.
    
    PROPERTIES:
        • kind: What aspect is being assessed (IdentityConsistencyAssessmentKind.*)
        • classification: Consistency status classification
        • aligned_components: Components that align
        • misaligned_components: Components that don't align
        • confidence: Confidence in assessment (0.0 to 1.0)
    """
    
    kind: str = ""
    """What aspect is being assessed (IdentityConsistencyAssessmentKind.*)."""
    
    classification: str = "consistent"
    """Consistency status classification:
       - consistent: All components align
       - mostly_consistent: Mostly align, minor issues
       - partially_consistent: Significant misalignments
       - inconsistent: Major conflicts
       - conflicted: Clear contradictions
       - undetermined: Cannot determine
    """
    
    aligned_components: Tuple[str, ...] = field(default_factory=tuple)
    """Component IDs that are consistent with each other."""
    
    misaligned_components: Tuple[str, ...] = field(default_factory=tuple)
    """Component IDs that don't align properly."""
    
    confidence: float = 1.0
    """Confidence in this assessment (0.0 to 1.0)."""