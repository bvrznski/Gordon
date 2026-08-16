# Correspondence Alternative - Phase 5.2.3
# =========================================

"""
Alternative correspondence interpretations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class CorrespondenceAlternative:
    """
    An alternative correspondence interpretation.
    
    Fields:
        alternative_identity: Unique identifier
        participating_artifacts: Which artifacts?
        proposed_correspondence_kind: What kind of correspondence?
        supporting_evidence: Evidence for this interpretation
        conflicting_evidence: Evidence against it
        confidence: Confidence in this alternative
        evidence_needed: What additional evidence would help?
    """
    
    alternative_identity: str
    
    participating_artifacts: Tuple[str, ...]
    
    proposed_correspondence_kind: str = "same_entity_candidate"
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    conflicting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence: float = 0.5
    
    evidence_needed: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CorrespondenceDimension:
    """
    A single correspondence dimension evaluation.
    
    Fields:
        dimension_name: Which dimension?
        score: Compatibility score (0.0-1.0)
        evidence: Supporting evidence
        limitations: Known limitations
    """
    
    dimension_name: str  # temporal, spatial, identity, etc.
    
    score: float = 1.0
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    limitations: Tuple[str, ...] = field(default_factory=tuple)