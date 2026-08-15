# Identity Coherence Assessment Model
# ====================================

"""
Immutable identity coherence assessment model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityCoherenceAssessment:
    """
    Immutable representation of an identity coherence assessment.
    
    PROPERTIES:
        • kind: What aspect is being assessed (IdentityCoherenceAssessmentKind.*)
        • classification: Coherence status classification
        • well_integrated_components: Components that are well-integrated
        • loosely_connected_components: Components with weak connections
        • unstructured_elements: Unstructured identity elements
        • confidence: Confidence in assessment (0.0 to 1.0)
    """
    
    kind: str = ""
    """What aspect is being assessed (IdentityCoherenceAssessmentKind.*)."""
    
    classification: str = "coherent"
    """Coherence status classification:
       - coherent: Well-organized identity structure
       - mostly_coherent: Mostly organized, some gaps
       - partially_coherent: Significant gaps or inconsistencies
       - incoherent: Poorly structured identity
       - unknown: Cannot determine
    """
    
    well_integrated_components: Tuple[str, ...] = field(default_factory=tuple)
    """Component IDs that are well-integrated."""
    
    loosely_connected_components: Tuple[str, ...] = field(default_factory=tuple)
    """Component IDs with weak or unclear connections."""
    
    unstructured_elements: Tuple[str, ...] = field(default_factory=tuple)
    """Identity elements without clear structure or context."""
    
    confidence: float = 1.0
    """Confidence in this assessment (0.0 to 1.0)."""