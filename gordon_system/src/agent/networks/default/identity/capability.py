# Identity Capability Assessment Model
# ====================================

"""
Immutable identity capability assessment model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityCapabilityAssessment:
    """
    Immutable representation of a capability self-assessment.
    
    PROPERTIES:
        • category: What category of capability (IdentityCapabilityAssessmentKind.*)
        • claimed_competence: Competence level claimed (0.0 to 1.0)
        • observed_performance_evidence: Evidence from actual performance
        • limitations: Known limitations on this capability
        • calibration: How well confidence matches actual competence
        • confidence: Confidence in this assessment (0.0 to 1.0)
        • effective_from_utc: When this assessment became active
        • source: Where the assessment came from
        • provenance: Provenance tracking
    """
    
    category: str  # IdentityCapabilityAssessmentKind.*
    """What category of capability (IdentityCapabilityAssessmentKind.*)."""
    
    claimed_competence: float = 0.5
    """Competence level claimed (0.0 to 1.0)."""
    
    observed_performance_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs from actual performance."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations on this capability."""
    
    calibration: float = 1.0
    """How well confidence matches actual competence (0.0 to 1.0)."""
    
    confidence: float = 1.0
    """Confidence in this assessment (0.0 to 1.0)."""
    
    effective_from_utc: datetime = field(default_factory=datetime.utcnow)
    """When this assessment became active."""
    
    source: str = "identity_self_assessment"
    """Where the assessment came from."""
    
    provenance: str = "canonical"
    """Provenance tracking reference."""