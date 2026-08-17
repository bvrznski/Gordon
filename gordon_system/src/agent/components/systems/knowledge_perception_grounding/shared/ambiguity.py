# Knowledge-Perception Grounding - Ambiguity Contract
# =====================================================

"""
Ambiguity: Explicit representation of perceptual uncertainty.

When multiple semantic interpretations remain plausible, ambiguity shall
remain explicit. Ambiguity is never silently resolved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# PERCEPT AMBIGUITY - Multiple interpretations of a single percept
# =============================================================================


@dataclass(frozen=True)
class PerceptAmbiguity:
    """
    Record of ambiguity in perceptual interpretation.
    
    When multiple semantic interpretations remain plausible for a percept,
    all candidates and their supporting observations shall remain explicit.
    
    Fields:
        ambiguity_identity:    Unique identifier
        
        percept:               Reference to the ambiguous percept
        alternatives:          Alternative interpretations (each with support)
        
        distinguishing_features: Features that could disambiguate
        confidence:            Confidence in each alternative (0.0-1.0)
        uncertainty:           Uncertainty about ambiguity resolution
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    ambiguity_identity: str
    
    # Percept reference (required)
    percept: str                   # Reference to the ambiguous percept
    
    # Alternatives (required)
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Each has: semantic_candidate_id, confidence
    
    # Disambiguation info
    distinguishing_features: Tuple[str, ...] = field(default_factory=tuple)  # Features to resolve ambiguity
    
    confidence: float = 0.5        # Average confidence across alternatives (0.0-1.0)
    uncertainty: float = 0.5       # Uncertainty about resolution (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate percept ambiguity."""
        if not self.ambiguity_identity:
            raise ValueError("ambiguity_identity is required")
        if len(self.alternatives) < 2:
            raise ValueError("Ambiguity must have at least 2 alternatives")
    
    @property
    def is_resolvable(self) -> bool:
        """Check if this ambiguity can be resolved with additional observations."""
        return (
            len(self.distinguishing_features) > 0 and
            self.confidence < 1.0 and
            self.uncertainty > 0.0
        )
    
    @property
    def is_high_confidence_disambiguation(self) -> bool:
        """Check if we have high confidence about the ambiguity itself."""
        return self.confidence >= 0.8
    
    @classmethod
    def create(
        cls,
        percept_id: str,
        alternative_interpretations: List[Dict[str, Any]],
        distinguishing_features: Optional[List[str]] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
    ) -> "PerceptAmbiguity":
        """Create a new percept ambiguity record."""
        return cls(
            ambiguity_identity=f"ambiguity:{uuid.uuid4().hex[:24]}",
            percept=percept_id,
            alternatives=tuple(alternative_interpretations),
            distinguishing_features=tuple(distinguishing_features or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ambiguity record to dictionary."""
        return {
            "ambiguity_identity": self.ambiguity_identity,
            "percept": self.percept,
            "alternatives": list(self.alternatives),
            "distinguishing_features": list(self.distinguishing_features),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# AMBIGUITY RESOLUTION - Process of disambiguating a percept
# =============================================================================


@dataclass(frozen=True)
class AmbiguityResolution:
    """
    Record of how an ambiguity was resolved.
    
    Fields:
        resolution_identity:   Unique identifier
        
        original_ambiguity:    Reference to the original ambiguity record
        resolution_method:     How was it resolved? (observation, reasoning, etc.)
        
        chosen_interpretation: Which interpretation was selected?
        rejected_alternatives: Which alternatives were rejected?
        
        supporting_evidence:   Evidence that supported the choice
        confidence_after:      Confidence after resolution (0.0-1.0)
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    resolution_identity: str
    
    # Original reference (required)
    original_ambiguity: str        # Reference to original ambiguity record
    
    # Resolution details (required)
    resolution_method: str         # e.g., "additional_observation", "reasoning"
    
    # Results
    chosen_interpretation: Dict[str, Any]  # The selected alternative
    rejected_alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Rejected options
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)  # Evidence for choice
    
    confidence_after: float = 1.0  # Confidence after resolution (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate ambiguity resolution."""
        if not self.resolution_identity:
            raise ValueError("resolution_identity is required")
        if not 0.0 <= self.confidence_after <= 1.0:
            raise ValueError(f"confidence_after must be 0.0-1.0, got {self.confidence_after}")
    
    @classmethod
    def create(
        cls,
        ambiguity_id: str,
        resolution_method: str = "additional_observation",
        chosen_interpretation: Optional[Dict[str, Any]] = None,
        rejected_alternatives: Optional[List[Dict[str, Any]]] = None,
        supporting_evidence_ids: Optional[List[str]] = None,
        confidence_after: float = 1.0,
    ) -> "AmbiguityResolution":
        """Create a new ambiguity resolution record."""
        return cls(
            resolution_identity=f"ambiguity_resolution:{uuid.uuid4().hex[:24]}",
            original_ambiguity=ambiguity_id,
            resolution_method=resolution_method,
            chosen_interpretation=chosen_interpretation or {},
            rejected_alternatives=tuple(rejected_alternatives or []),
            supporting_evidence=tuple(supporting_evidence_ids or []),
            confidence_after=max(0.0, min(1.0, float(confidence_after))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resolution record to dictionary."""
        return {
            "resolution_identity": self.resolution_identity,
            "original_ambiguity": self.original_ambiguity,
            "resolution_method": self.resolution_method,
            "chosen_interpretation": dict(self.chosen_interpretation),
            "rejected_alternatives_count": len(self.rejected_alternatives),
            "supporting_evidence_count": len(self.supporting_evidence),
            "confidence_after": self.confidence_after,
        }


# =============================================================================
# AMBIGUITY GROUP - Group of related ambiguities
# =============================================================================


@dataclass(frozen=True)
class AmbiguityGroup:
    """
    Groups related ambiguities that may be resolved together.
    
    Fields:
        group_identity:        Unique identifier
        
        member_ambiguities:    References to the grouped ambiguity records
        
        grouping_reason:       Why were these grouped? (e.g., "same_entity", "temporal_coherence")
        
        proposed_resolution_strategy: How might they be resolved together?
        
        confidence:            Confidence in this group (0.0-1.0)
        uncertainty:           Uncertainty about group boundaries
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    group_identity: str
    
    # Group members (required)
    member_ambiguities: Tuple[str, ...]  # Ambiguity record IDs
    
    # Grouping description (required)
    grouping_reason: str           # e.g., "same_entity", "temporal_coherence"
    
    # Resolution strategy
    proposed_resolution_strategy: Dict[str, Any] = field(default_factory=dict)  # Strategy details
    
    confidence: float = 1.0        # Group confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about grouping
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate ambiguity group."""
        if not self.group_identity:
            raise ValueError("group_identity is required")
        if len(self.member_ambiguities) < 2:
            raise ValueError("AmbiguityGroup must contain at least 2 ambiguities")
    
    @classmethod
    def create(
        cls,
        ambiguity_ids: List[str],
        grouping_reason: str = "same_entity",
        proposed_strategy: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "AmbiguityGroup":
        """Create a new ambiguity group."""
        return cls(
            group_identity=f"ambiguity_group:{uuid.uuid4().hex[:24]}",
            member_ambiguities=tuple(ambiguity_ids),
            grouping_reason=grouping_reason,
            proposed_resolution_strategy=proposed_strategy or {},
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert group to dictionary."""
        return {
            "group_identity": self.group_identity,
            "member_ambiguities": list(self.member_ambiguities),
            "grouping_reason": self.grouping_reason,
            "proposed_resolution_strategy": dict(self.proposed_resolution_strategy),
            "confidence": self.confidence,
        }


# =============================================================================
# AMBIGUITY CONTEXT - Context in which ambiguity exists
# =============================================================================


@dataclass(frozen=True)
class AmbiguityContext:
    """
    Context information for understanding ambiguity.
    
    Fields:
        context_identity:      Unique identifier
        
        percept:               Reference to the ambiguous percept
        environment:           Environment description during observation
        
        temporal_context:      Time window (start, end timestamps)
        spatial_context:       Spatial region if applicable
        
        sensory_inputs:        Multiple sensory inputs that contributed
        interpretation_scope:  What aspects are ambiguous?
        
        confidence:            Confidence in this context (0.0-1.0)
        uncertainty:           Uncertainty about context
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    context_identity: str
    
    # Percept reference (required)
    percept: str                   # Reference to the ambiguous percept
    
    # Context description
    environment: str = ""          # Environment description
    temporal_context_start_utc: float = 0.0  # Start time
    temporal_context_end_utc: float = 0.0    # End time
    
    spatial_context: Optional[Tuple[float, float]] = None  # x,y location if applicable
    
    sensory_inputs: Tuple[str, ...] = field(default_factory=tuple)  # Input IDs
    
    interpretation_scope: str = ""  # e.g., "object_identity", "action_type"
    
    confidence: float = 1.0        # Context confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about context
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate ambiguity context."""
        if not self.context_identity:
            raise ValueError("context_identity is required")
    
    @property
    def duration_sec(self) -> float:
        """Get temporal context duration in seconds."""
        return self.temporal_context_end_utc - self.temporal_context_start_utc
    
    @classmethod
    def create(
        cls,
        percept_id: str,
        environment: str = "",
        temporal_start: float = 0.0,
        temporal_end: float = 0.0,
        spatial_location: Optional[Tuple[float, float]] = None,
        sensory_input_ids: Optional[List[str]] = None,
        interpretation_scope: str = "",
        confidence: float = 1.0,
    ) -> "AmbiguityContext":
        """Create a new ambiguity context."""
        return cls(
            context_identity=f"ambiguity_context:{uuid.uuid4().hex[:24]}",
            percept=percept_id,
            environment=environment,
            temporal_context_start_utc=temporal_start,
            temporal_context_end_utc=temporal_end,
            spatial_context=spatial_location,
            sensory_inputs=tuple(sensory_input_ids or []),
            interpretation_scope=interpretation_scope,
            confidence=max(0.0, min(1.0, float(confidence))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "context_identity": self.context_identity,
            "percept": self.percept,
            "environment": self.environment,
            "temporal_context_start_utc": self.temporal_context_start_utc,
            "temporal_context_end_utc": self.temporal_context_end_utc,
            "spatial_context": list(self.spatial_context) if self.spatial_context else None,
            "sensory_inputs_count": len(self.sensory_inputs),
            "interpretation_scope": self.interpretation_scope,
            "confidence": self.confidence,
        }


__all__ = [
    "PerceptAmbiguity",
    "AmbiguityResolution",
    "AmbiguityGroup",
    "AmbiguityContext",
]
