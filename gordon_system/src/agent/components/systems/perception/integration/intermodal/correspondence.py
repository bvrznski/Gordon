# Intermodal Correspondence - Phase 5.2.3
# ========================================

"""
Core intermodal correspondence evaluation logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class IntermodalCorrespondence:
    """
    A correspondence relationship between artifacts from different modalities.
    
    Fields:
        correspondence_identity: Unique identifier
        participating_artifacts: Which artifacts correspond?
        participating_modalities: Modalities involved
        correspondence_kind: What kind of correspondence?
        supporting_evidence: Evidence for this correspondence
        conflicting_evidence: Evidence against it
        temporal_compatibility: How compatible in time? (0.0-1.0)
        spatial_compatibility: How compatible in space? (0.0-1.0)
        identity_compatibility: How similar are identities?
        source_independence: Are sources independent?
    """
    
    correspondence_identity: str
    
    participating_artifacts: Tuple[str, ...]
    participating_modalities: Tuple[str, ...]
    
    correspondence_kind: str = "same_event_candidate"
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    conflicting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    temporal_compatibility: float = 1.0
    spatial_compatibility: float = 1.0
    identity_compatibility: float = 1.0
    
    source_independence: str = "unknown"
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    alternatives: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


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
    
    evidence_kind: str = "unknown"
    
    supporting_features: Tuple[str, ...] = field(default_factory=tuple)
    conflicting_features: Tuple[str, ...] = field(default_factory=tuple)
    
    source_dependency: Optional[str] = None
    temporal_scope: Dict[str, Any] = field(default_factory=dict)
    spatial_scope: Dict[str, Any] = field(default_factory=dict)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
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


# Correspondence kinds
CORRESPONDENCE_KINDS = {
    "same_entity_candidate": "Artifacts refer to the same entity",
    "same_event_candidate": "Artifacts refer to the same event",
    "same_state_candidate": "Artifacts describe the same state",
    "same_utterance_candidate": "Artifacts represent the same utterance",
    "same_command_execution_candidate": "Artifacts track the same command execution",
    "same_file_change_candidate": "Artifacts record the same file change",
    "same_process_activity_candidate": "Artifacts show the same process activity",
    "derived_view": "One is a derived view of the other",
    "supporting_evidence": "Evidence supports the same claim",
    "conflicting_evidence": "Evidence contradicts each other",
    "related_but_distinct": "Related but refer to different things",
}