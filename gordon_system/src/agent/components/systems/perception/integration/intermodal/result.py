# Intermodal Correspondence Result - Phase 5.2.3
# ==============================================

"""
Correspondence Result: Outcome of correspondence evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class IntermodalCorrespondenceResult:
    """
    Result of intermodal correspondence evaluation.
    
    Fields:
        request_reference: Reference to the original request
        correspondences: Found correspondences
        alternatives: Alternative interpretations considered
        rejected_candidates: Candidates that were rejected
        supporting_evidence: Evidence for found correspondences
        conflicting_evidence: Evidence against some correspondences
        confidence: Overall confidence in results
        uncertainty: Known limitations
        status: Execution status
    """
    
    request_reference: str
    
    correspondences: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    rejected_candidates: Tuple[str, ...] = field(default_factory=tuple)
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    conflicting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    status: str = "unknown"  # See Status enum
    
    provenance: Dict[str, Any] = field(default_factory=dict)


class CorrespondenceStatus:
    """Status of correspondence evaluation."""
    ESTABLISHED_CANDIDATE = "established_candidate"
    PARTIAL = "partial"
    AMBIGUOUS = "ambiguous"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNKNOWN = "unknown"


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
    
    evidence_kind: str = "unknown"  # See EvidenceKind enum
    
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
    UNKNOWN = "unknown"


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
class IntermodalCorrespondence:
    """
    A correspondence relationship between artifacts.
    
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
    
    source_independence: str = "unknown"  # independent, partially_dependent, derived_from_common_source, duplicated
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    alternatives: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


class CorrespondenceKind:
    """Kinds of correspondence relationships."""
    SAME_ENTITY_CANDIDATE = "same_entity_candidate"
    SAME_EVENT_CANDIDATE = "same_event_candidate"
    SAME_STATE_CANDIDATE = "same_state_candidate"
    SAME_UTTERANCE_CANDIDATE = "same_utterance_candidate"
    SAME_COMMAND_EXECUTION_CANDIDATE = "same_command_execution_candidate"
    SAME_FILE_CHANGE_CANDIDATE = "same_file_change_candidate"
    SAME_PROCESS_ACTIVITY_CANDIDATE = "same_process_activity_candidate"
    DERIVED_VIEW = "derived_view"
    SUPPORTING_EVIDENCE = "supporting_evidence"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    RELATED_BUT_DISTINCT = "related_but_distinct"
    UNKNOWN = "unknown"