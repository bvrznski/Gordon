# Correspondence Evidence - Phase 5.2.3
# ======================================

"""
Correspondence evidence types and helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class CorrespondenceEvidence:
    """
    Evidence supporting or rejecting a correspondence.
    
    Fields:
        evidence_identity: Unique identifier
        candidate_artifacts: Artifacts involved
        evidence_kind: What type of evidence?
        supporting_features: Features that support this
        conflicting_features: Features that conflict
        source_dependency: Reference to dependency assessment
        temporal_scope: When was this observed?
        spatial_scope: Where was this observed?
    """
    
    evidence_identity: str
    
    candidate_artifacts: Tuple[str, ...]
    
    evidence_kind: str = "unknown"  # See EvidenceKind
    
    supporting_features: Tuple[str, ...] = field(default_factory=tuple)
    conflicting_features: Tuple[str, ...] = field(default_factory=tuple)
    
    source_dependency: Optional[str] = None
    temporal_scope: Dict[str, Any] = field(default_factory=dict)
    spatial_scope: Dict[str, Any] = field(default_factory=dict)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    provenance: Dict[str, Any] = field(default_factory=dict)


class EvidenceKind:
    """Kinds of correspondence evidence."""
    
    IDENTIFIER_MATCH = "identifier_match"
    TIME_OVERLAP = "time_overlap"
    SPATIAL_OVERLAP = "spatial_overlap"
    CONTENT_MATCH = "content_match"
    LABEL_MATCH = "label_match"
    PATH_MATCH = "path_match"
    PROCESS_RELATION = "process_relation"
    WINDOW_RELATION = "window_relation"
    UTTERANCE_MATCH = "utterance_match"
    EVENT_STRUCTURE_MATCH = "event_structure_match"
    FINGERPRINT_MATCH = "fingerprint_match"
    EXPLICIT_EXTERNAL_LINK = "explicit_external_link"