# Salience Network Uncertainty State
# ===================================
#
# Canonical implementation of semantic uncertainty (Phase 4.8.4).
#

"""
Uncertainty representation for Salience State.

UNCERTAINTY vs CONFIDENCE:
    - Uncertainty describes unresolved semantic unknowns
    - Confidence describes strength of belief in the assessment
    
A State can have:
    - Low uncertainty + low confidence = insufficient support for assessment
    - High uncertainty + high confidence = clear that domain is unresolved

UNIVERSAL INVARIANTS:
    - SALIENCE-UNCERTAINTY-INV-001: Uncertainty and confidence are distinct
    - SALIENCE-UNCERTAINTY-INV-002: Missing evidence produces uncertainty
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SalienceUncertaintyState:
    """
    Canonical semantic uncertainty representation.
    
    UNCERTAINTY CATEGORIES:
        - KNOWN: Semantic status is determined
        - PARTIALLY_KNOWN: Some information available but incomplete
        - AMBIGUOUS: Multiple interpretations equally plausible
        - CONFLICTED: Contradictory evidence present
        - UNKNOWN: No basis for assessment
        - INDETERMINATE: Cannot be determined by current methods
    
    UNCERTAINTY LAWS:
        - SALIENCE-UNCERTAINTY-LAW-001: Unknown is not negligible
        - SALIENCE-UNCERTAINTY-LAW-002: Missing evidence produces uncertainty
        - SALIENCE-UNCERTAINTY-LAW-003: Contradictory evidence creates conflict
    
    UNCERTAINTY COMPOSITION:
        - missing_evidence_ids: Content identities lacking evaluation
        - conflicting_evidence_ids: Evidence with mutually exclusive conclusions
        - uncertain_subjects: Subjects whose status cannot be determined
    """
    
    category: str = field(default="unknown")
    """Semantic uncertainty category."""
    
    confidence: str = field(default="unknown")
    """Strength of belief in the assessment (distinct from uncertainty)."""
    
    missing_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of Content items that lack evaluation."""
    
    conflicting_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of evidence with mutually exclusive conclusions."""
    
    uncertain_subjects: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of subjects whose salience status cannot be determined."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """
    Semantic basis for the uncertainty classification:
        - Evidence gaps
        - Methodological limitations
        - External constraints
    """
    
    @property
    def has_unknown(self) -> bool:
        """Indicates whether semantic unknowns are present."""
        return self.category in ("unknown", "incomplete", "ambiguous", "conflicted")