# Knowledge-Perception Grounding - Grounding Records and Semantic Candidates
# =========================================================================

"""
Grounding: Connection between semantic knowledge and current perception.

This module defines:
- Grounded events (perceptually grounded temporal sequences)
- Knowledge-grounding records (linking knowledge to perceptions)
- Semantic candidates (proposed meanings from percepts)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# GROUNDING KINDS - What kind of grounding relationship is this?
# =============================================================================


class GroundingKind(Enum):
    """
    Kinds of grounding relationships between knowledge and perception.
    
    DIRECT: Direct correspondence to current observations
    HISTORICAL: Based on remembered patterns from past observations
    ANALOGICAL: Borrowed from similar prior situations
    DERIVED: Derived through reasoning from other grounded knowledge
    UNKNOWN: Uncertain or undetermined grounding kind
    """
    
    DIRECT = "direct"
    HISTORICAL = "historical"
    ANALOGICAL = "analogical"
    DERIVED = "derived"
    UNKNOWN = "unknown"


# =============================================================================
# GROUNDED EVENT - Perceptually grounded event sequence
# =============================================================================


@dataclass(frozen=True)
class GroundedEvent:
    """
    Event constructed from perceptual evidence.
    
    Events are temporal sequences of percepts that form a coherent
    perceptual event. They remain perceptual (not semantic) but may
    generate semantic candidates.
    
    Fields:
        event_identity:        Unique identifier
        
        supporting_percepts:   References to percepts forming this event
        event_structure:       Temporal/spatial structure description
        
        temporal_extent_start_utc: Start time of the event
        temporal_extent_end_utc:   End time of the event
        
        spatial_extent:        Spatial region if applicable (optional)
        participants:          Participant entities identified (optional)
        
        candidate_semantics:   Proposed semantic interpretations (references)
        confidence:            Confidence in this event (0.0-1.0)
        uncertainty:           Uncertainty about this event
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    event_identity: str
    
    # Percept references (required)
    supporting_percepts: Tuple[str, ...]  # References to percepts
    
    # Structure description
    event_structure: Dict[str, Any] = field(default_factory=dict)  # Temporal sequence info
    
    # Temporal extent
    temporal_extent_start_utc: float = 0.0
    temporal_extent_end_utc: float = 0.0
    
    # Spatial context
    spatial_extent: Optional[Tuple[float, float, float, float]] = None  # x1,y1,x2,y2
    
    # Participants
    participants: Tuple[str, ...] = field(default_factory=tuple)  # Entity references
    
    # Semantic candidates
    candidate_semantics: Tuple[str, ...] = field(default_factory=tuple)  # Candidate IDs
    
    # Quality metrics (required)
    confidence: float = 1.0        # Event confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about event
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate grounded event."""
        if not self.event_identity:
            raise ValueError("event_identity is required")
        if len(self.supporting_percepts) == 0:
            raise ValueError("GroundedEvent must have at least one supporting percept")
    
    @property
    def duration_sec(self) -> float:
        """Get event duration in seconds."""
        return self.temporal_extent_end_utc - self.temporal_extent_start_utc
    
    @property
    def is_valid(self) -> bool:
        """Check if event has minimal required data."""
        return (
            len(self.event_identity) > 0 and
            len(self.supporting_percepts) > 0 and
            self.duration_sec >= 0.0
        )
    
    @classmethod
    def create(
        cls,
        percept_ids: List[str],
        event_structure: Optional[Dict[str, Any]] = None,
        temporal_start_utc: float = 0.0,
        temporal_end_utc: float = 0.0,
        spatial_extent: Optional[Tuple[float, float, float, float]] = None,
        participants: Optional[List[str]] = None,
        candidate_semantics: Optional[List[str]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "GroundedEvent":
        """Create a new grounded event."""
        return cls(
            event_identity=f"grounded_event:{uuid.uuid4().hex[:24]}",
            supporting_percepts=tuple(percept_ids),
            event_structure=event_structure or {},
            temporal_extent_start_utc=temporal_start_utc,
            temporal_extent_end_utc=temporal_end_utc,
            spatial_extent=spatial_extent,
            participants=tuple(participants or []),
            candidate_semantics=tuple(candidate_semantics or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_identity": self.event_identity,
            "supporting_percepts": list(self.supporting_percepts),
            "event_structure": dict(self.event_structure),
            "temporal_extent_start_utc": self.temporal_extent_start_utc,
            "temporal_extent_end_utc": self.temporal_extent_end_utc,
            "spatial_extent": list(self.spatial_extent) if self.spatial_extent else None,
            "participants": list(self.participants),
            "candidate_semantics": list(self.candidate_semantics),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# KNOWLEDGE-PERCEPTION GROUNDING RECORD - Link knowledge to perception
# =============================================================================


@dataclass(frozen=True)
class KnowledgePerceptionGrounding:
    """
    Record linking a Knowledge Artifact to current perceptual evidence.
    
    Grounding records show how semantic knowledge is connected to present reality.
    
    Fields:
        grounding_identity:    Unique identifier
        
        knowledge_artifact:    Reference to the knowledge artifact
        percepts:              References to supporting percepts
        observations:          References to supporting observations (optional)
        
        grounding_kind:        What kind of grounding relationship?
        
        support_strength:      How strongly do percepts support this? (0.0-1.0)
        contradiction_strength: How strong are contradictions? (0.0-1.0)
        
        temporal_scope_start_utc: When is this grounding valid from?
        temporal_scope_end_utc:   When is this grounding valid until?
        
        confidence:            Confidence in this grounding (0.0-1.0)
        uncertainty:           Uncertainty about this grounding
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    grounding_identity: str
    
    # Knowledge reference (required)
    knowledge_artifact: str        # Reference to knowledge artifact
    
    # Perceptual evidence (required)
    percepts: Tuple[str, ...]      # Supporting percept IDs
    
    # Grounding description (required) - before defaults
    grounding_kind: str            # e.g., "direct", "historical"
    
    observations: Tuple[str, ...] = field(default_factory=tuple)  # Optional observation refs
    
    # Strength metrics
    support_strength: float = 0.5  # Evidence support strength (0.0-1.0)
    contradiction_strength: float = 0.0  # Contradiction strength (0.0-1.0)
    
    # Temporal scope
    temporal_scope_start_utc: Optional[float] = None
    temporal_scope_end_utc: Optional[float] = None
    
    # Quality metrics (required) - before defaults
    confidence: float = 0.5        # Grounding confidence (0.0-1.0)
    uncertainty: float = 0.5       # Uncertainty about grounding
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate grounding record."""
        if not self.grounding_identity:
            raise ValueError("grounding_identity is required")
        if len(self.percepts) == 0:
            raise ValueError("Grounding must reference at least one percept")
    
    @property
    def is_strong_grounding(self) -> bool:
        """Check if this grounding has strong support."""
        return self.support_strength >= 0.7 and self.contradiction_strength < 0.3
    
    @property
    def is_weak_grounding(self) -> bool:
        """Check if this grounding has weak support."""
        return self.support_strength < 0.5 or self.contradiction_strength > 0.3
    
    @classmethod
    def create(
        cls,
        knowledge_artifact_ref: str,
        percept_ids: List[str],
        grounding_kind: GroundingKind = GroundingKind.UNKNOWN,
        observation_ids: Optional[List[str]] = None,
        support_strength: float = 0.5,
        contradiction_strength: float = 0.0,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
    ) -> "KnowledgePerceptionGrounding":
        """Create a new grounding record."""
        return cls(
            grounding_identity=f"grounding:{uuid.uuid4().hex[:24]}",
            knowledge_artifact=knowledge_artifact_ref,
            percepts=tuple(percept_ids),
            observations=tuple(observation_ids or []),
            grounding_kind=grounding_kind.value if isinstance(grounding_kind, Enum) else grounding_kind,
            support_strength=max(0.0, min(1.0, float(support_strength))),
            contradiction_strength=max(0.0, min(1.0, float(contradiction_strength))),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert grounding to dictionary."""
        return {
            "grounding_identity": self.grounding_identity,
            "knowledge_artifact": self.knowledge_artifact,
            "percepts": list(self.percepts),
            "observations": list(self.observations),
            "grounding_kind": self.grounding_kind,
            "support_strength": self.support_strength,
            "contradiction_strength": self.contradiction_strength,
            "temporal_scope_start_utc": self.temporal_scope_start_utc,
            "temporal_scope_end_utc": self.temporal_scope_end_utc,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# GROUNDING REQUEST - Request for grounding assessment
# =============================================================================


@dataclass(frozen=True)
class KnowledgePerceptionGroundingRequest:
    """
    Request to assess or create grounding for a knowledge artifact.
    
    Fields:
        request_identity:      Unique identifier
        
        knowledge_artifact:    Reference to the knowledge artifact needing grounding
        supporting_percepts:   References to percepts that might support this
        
        temporal_scope_start_utc: Start of relevant time window (optional)
        temporal_scope_end_utc:   End of relevant time window (optional)
        
        grounding_policy:      How should grounding be assessed? (e.g., "strict", "liberal")
        contradiction_policy:  How should contradictions be handled?
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    request_identity: str
    
    # Knowledge reference (required)
    knowledge_artifact: str        # Reference to artifact needing grounding
    
    # Supporting evidence
    supporting_percepts: Tuple[str, ...] = field(default_factory=tuple)  # Percept IDs
    
    # Temporal scope
    temporal_scope_start_utc: Optional[float] = None
    temporal_scope_end_utc: Optional[float] = None
    
    # Policies (required)
    grounding_policy: str = "strict"       # e.g., "strict", "liberal"
    contradiction_policy: str = "report"   # e.g., "report", "override", "flag"
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate grounding request."""
        if not self.request_identity:
            raise ValueError("request_identity is required")
    
    @classmethod
    def create(
        cls,
        knowledge_artifact_ref: str,
        supporting_percept_ids: Optional[List[str]] = None,
        temporal_start_utc: Optional[float] = None,
        temporal_end_utc: Optional[float] = None,
        grounding_policy: str = "strict",
        contradiction_policy: str = "report",
    ) -> "KnowledgePerceptionGroundingRequest":
        """Create a new grounding request."""
        return cls(
            request_identity=f"grounding_request:{uuid.uuid4().hex[:24]}",
            knowledge_artifact=knowledge_artifact_ref,
            supporting_percepts=tuple(supporting_percept_ids or []),
            temporal_scope_start_utc=temporal_start_utc,
            temporal_scope_end_utc=temporal_end_utc,
            grounding_policy=grounding_policy,
            contradiction_policy=contradiction_policy,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_identity": self.request_identity,
            "knowledge_artifact": self.knowledge_artifact,
            "supporting_percepts": list(self.supporting_percepts),
            "temporal_scope_start_utc": self.temporal_scope_start_utc,
            "temporal_scope_end_utc": self.temporal_scope_end_utc,
            "grounding_policy": self.grounding_policy,
            "contradiction_policy": self.contradiction_policy,
        }


# =============================================================================
# GROUNDING ASSESSMENT - Assessment of grounding quality
# =============================================================================


@dataclass(frozen=True)
class KnowledgePerceptionGroundingAssessment:
    """
    Assessment of how well a knowledge artifact is grounded in perception.
    
    Fields:
        assessment_identity:   Unique identifier
        
        knowledge_artifact:    Reference to the assessed knowledge artifact
        
        supporting_percepts:   References to percepts that support this
        contradicting_percepts: References to percepts that contradict this
        
        grounding_strength:    Overall strength of grounding (0.0-1.0)
        temporal_validity:     How long is this grounding valid? (in seconds)
        
        confidence:            Confidence in assessment (0.0-1.0)
        uncertainty:           Uncertainty about this assessment
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    assessment_identity: str
    
    # Knowledge reference (required)
    knowledge_artifact: str        # Reference to assessed artifact
    
    # Evidence references
    supporting_percepts: Tuple[str, ...] = field(default_factory=tuple)  # Supporting percept IDs
    contradicting_percepts: Tuple[str, ...] = field(default_factory=tuple)  # Contradicting percept IDs
    
    # Assessment metrics (required)
    grounding_strength: float = 0.5  # Strength of grounding (0.0-1.0)
    temporal_validity: float = 0.0   # Validity duration in seconds
    
    confidence: float = 1.0        # Assessment confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about assessment
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate grounding assessment."""
        if not self.assessment_identity:
            raise ValueError("assessment_identity is required")
    
    @property
    def net_grounding_strength(self) -> float:
        """Calculate net grounding strength (support - contradiction)."""
        support = len(self.supporting_percepts)
        contradict = len(self.contradicting_percepts)
        total = support + contradict
        if total == 0:
            return 0.0
        return (support - contradict) / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "assessment_identity": self.assessment_identity,
            "knowledge_artifact": self.knowledge_artifact,
            "supporting_percepts": list(self.supporting_percepts),
            "contradicting_percepts": list(self.contradicting_percepts),
            "grounding_strength": self.grounding_strength,
            "temporal_validity": self.temporal_validity,
            "confidence": self.confidence,
        }


# =============================================================================
# SEMANTIC CANDIDATE KINDS - Types of semantic candidates
# =============================================================================


class SemanticCandidateKind(Enum):
    """
    Kinds of semantic candidates produced by grounding.
    
    ASSERTION: A claim about the world
    CONCEPT: A potential new concept from novelty
    RELATION: A proposed relationship between entities
    HYPOTHESIS: An explanatory hypothesis
    EVENT: A candidate event interpretation
    MODEL: A potential structural model
    UNKNOWN: Undetermined candidate kind
    """
    
    ASSERTION = "assertion"
    CONCEPT = "concept"
    RELATION = "relation"
    HYPOTHESIS = "hypothesis"
    EVENT = "event"
    MODEL = "model"
    UNKNOWN = "unknown"


# =============================================================================
# SEMANTIC CANDIDATE - Proposed semantic interpretation
# =============================================================================


@dataclass(frozen=True)
class SemanticCandidate:
    """
    Proposed semantic meaning from perceptual evidence.
    
    Candidates require Knowledge validation before becoming accepted knowledge.
    
    Fields:
        candidate_identity:    Unique identifier
        
        percept_basis:         References to percepts forming the basis
        proposed_semantics:    What is being proposed?
        
        supporting_observations: References to observations (optional)
        alternatives:          Alternative interpretations (optional)
        
        confidence:            Confidence in this candidate (0.0-1.0)
        uncertainty:           Uncertainty about this candidate
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    candidate_identity: str
    
    # Percept basis (required)
    percept_basis: Tuple[str, ...]  # References to percepts
    
    # Proposed meaning (required)
    proposed_semantics: Dict[str, Any] = field(default_factory=dict)  # Semantic content
    
    # Evidence
    supporting_observations: Tuple[str, ...] = field(default_factory=tuple)  # Optional obs refs
    
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Alternative interpretations
    
    # Quality metrics (required)
    confidence: float = 1.0        # Candidate confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about candidate
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate semantic candidate."""
        if not self.candidate_identity:
            raise ValueError("candidate_identity is required")
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this candidate has high confidence."""
        return self.confidence >= 0.8 and self.uncertainty < 0.2
    
    @classmethod
    def create(
        cls,
        percept_ids: List[str],
        proposed_semantics: Dict[str, Any],
        supporting_observation_ids: Optional[List[str]] = None,
        alternatives: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "SemanticCandidate":
        """Create a new semantic candidate."""
        return cls(
            candidate_identity=f"semantic_candidate:{uuid.uuid4().hex[:24]}",
            percept_basis=tuple(percept_ids),
            proposed_semantics=proposed_semantics,
            supporting_observations=tuple(supporting_observation_ids or []),
            alternatives=tuple(alternatives or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary."""
        return {
            "candidate_identity": self.candidate_identity,
            "percept_basis": list(self.percept_basis),
            "proposed_semantics": dict(self.proposed_semantics),
            "supporting_observations": list(self.supporting_observations),
            "alternatives_count": len(self.alternatives),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


__all__ = [
    "GroundingKind",
    "GroundedEvent",
    "KnowledgePerceptionGrounding",
    "KnowledgePerceptionGroundingRequest",
    "KnowledgePerceptionGroundingAssessment",
    "SemanticCandidateKind",
    "SemanticCandidate",
]