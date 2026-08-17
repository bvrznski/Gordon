# Knowledge-Perception Grounding - Active Perception & Reality Validation
# ========================================================================

"""
Active Perception and Reality Validation: Mechanisms for knowledge to request
additional perception or validate existing beliefs against current evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# ACTIVE PERCEPTION - Knowledge-driven perception requests
# =============================================================================


class ActivePerceptionOutcome(Enum):
    """
    Possible outcomes of an active perception request.
    
    COMPLETE: All requested observations were acquired successfully
    PARTIAL: Some but not all observations were acquired
    FAILED: Request failed to produce any results
    BLOCKED: Request was blocked (e.g., sensor unavailable)
    TIMEOUT: Request timed out before completion
    """
    
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


# =============================================================================
# ACTIVE PERCEPTION REQUEST - Knowledge requests additional perception
# =============================================================================


@dataclass(frozen=True)
class ActivePerceptionRequest:
    """
    Request from Knowledge to acquire additional observations.
    
    Fields:
        request_identity:      Unique identifier
        
        triggering_knowledge_artifact: Which knowledge artifact triggered this?
        
        missing_information:   What specific information is needed?
        requested_modalities:  Which sensor modalities are needed?
        
        requested_regions:     Spatial regions of interest (optional)
        requested_duration:    How long should observations be acquired? (seconds)
        requested_resolution:  Required quality/resolution
        
        priority:              Request priority (0.0-1.0, higher = more urgent)
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    request_identity: str
    
    # Trigger (required)
    triggering_knowledge_artifact: str  # Reference to knowledge artifact
    
    # Information needs (required)
    missing_information: str           # Description of what's needed
    
    requested_modalities: Tuple[str, ...] = field(default_factory=tuple)  # e.g., ["vision", "audio"]
    
    # Request parameters
    requested_regions: Optional[Tuple[float, float, float, float]] = None  # x,y,width,height or time range
    requested_duration: float = 1.0      # Duration in seconds
    requested_resolution: str = "high"   # e.g., "low", "medium", "high"
    
    # Priority (required)
    priority: float = 0.5              # Request priority (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate active perception request."""
        if not self.request_identity:
            raise ValueError("request_identity is required")
        if not 0.0 <= self.priority <= 1.0:
            raise ValueError(f"Priority must be 0.0-1.0, got {self.priority}")
    
    @classmethod
    def create(
        cls,
        knowledge_artifact_ref: str,
        missing_info_description: str,
        modalities: Optional[List[str]] = None,
        regions: Optional[Tuple[float, float, float, float]] = None,
        duration_sec: float = 1.0,
        resolution: str = "high",
        priority: float = 0.5,
    ) -> "ActivePerceptionRequest":
        """Create a new active perception request."""
        return cls(
            request_identity=f"active_perception_request:{uuid.uuid4().hex[:24]}",
            triggering_knowledge_artifact=knowledge_artifact_ref,
            missing_information=missing_info_description,
            requested_modalities=tuple(modalities or ["vision"]),
            requested_regions=regions,
            requested_duration=duration_sec,
            requested_resolution=resolution,
            priority=max(0.0, min(1.0, float(priority))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_identity": self.request_identity,
            "triggering_knowledge_artifact": self.triggering_knowledge_artifact,
            "missing_information": self.missing_information,
            "requested_modalities": list(self.requested_modalities),
            "requested_regions": list(self.requested_regions) if self.requested_regions else None,
            "requested_duration": self.requested_duration,
            "requested_resolution": self.requested_resolution,
            "priority": self.priority,
        }


# =============================================================================
# ACTIVE PERCEPTION RESPONSE - Perception's response to a request
# =============================================================================


@dataclass(frozen=True)
class ActivePerceptionResponse:
    """
    Response from Perception to an active perception request.
    
    Fields:
        response_identity:     Unique identifier
        
        request_reference:     Reference to the original request
        
        acquisition_result:    What was actually acquired?
        
        new_observations:      References to newly acquired observations
        new_percepts:          References to newly constructed percepts
        
        confidence:            Confidence in acquired data (0.0-1.0)
        uncertainty:           Uncertainty about results
        limitations:           Known limitations of this acquisition
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    response_identity: str
    
    # Request reference (required)
    request_reference: str         # Reference to the original request
    
    # Acquisition status (required)
    acquisition_result: ActivePerceptionOutcome  # What happened?
    
    # Results
    new_observations: Tuple[str, ...] = field(default_factory=tuple)  # Observation IDs
    new_percepts: Tuple[str, ...] = field(default_factory=tuple)      # Percept IDs
    
    confidence: float = 1.0        # Acquisition confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about results
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known issues
    diagnostics: Dict[str, Any] = field(default_factory=dict)     # Diagnostic info
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate active perception response."""
        if not self.response_identity:
            raise ValueError("response_identity is required")
    
    @property
    def is_success(self) -> bool:
        """Check if acquisition completed successfully."""
        return self.acquisition_result == ActivePerceptionOutcome.COMPLETE
    
    @property
    def is_partial(self) -> bool:
        """Check if acquisition was partial."""
        return self.acquisition_result == ActivePerceptionOutcome.PARTIAL
    
    @classmethod
    def success(
        cls,
        request_ref: str,
        observation_ids: Optional[List[str]] = None,
        percept_ids: Optional[List[str]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "ActivePerceptionResponse":
        """Create a successful response."""
        return cls(
            response_identity=f"active_perception_response:{uuid.uuid4().hex[:24]}",
            request_reference=request_ref,
            acquisition_result=ActivePerceptionOutcome.COMPLETE,
            new_observations=tuple(observation_ids or []),
            new_percepts=tuple(percept_ids or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    @classmethod
    def partial(
        cls,
        request_ref: str,
        observation_ids: List[str],
        missing_count: int,
        limitations: Optional[List[str]] = None,
    ) -> "ActivePerceptionResponse":
        """Create a partial success response."""
        return cls(
            response_identity=f"active_perception_response:{uuid.uuid4().hex[:24]}",
            request_reference=request_ref,
            acquisition_result=ActivePerceptionOutcome.PARTIAL,
            new_observations=tuple(observation_ids),
            confidence=0.5,  # Reduced for partial results
            uncertainty=0.3,  # Increased due to missing evidence
            limitations=tuple(limitations or ["Some observations unavailable"]),
        )
    
    @classmethod
    def failed(
        cls,
        request_ref: str,
        failure_reason: str,
    ) -> "ActivePerceptionResponse":
        """Create a failed response."""
        return cls(
            response_identity=f"active_perception_response:{uuid.uuid4().hex[:24]}",
            request_reference=request_ref,
            acquisition_result=ActivePerceptionOutcome.FAILED,
            limitations=(failure_reason,),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "response_identity": self.response_identity,
            "request_reference": self.request_reference,
            "acquisition_result": self.acquisition_result.value,
            "new_observations_count": len(self.new_observations),
            "new_percepts_count": len(self.new_percepts),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
        }


# =============================================================================
# REALITY VALIDATION - Validate knowledge against current perception
# =============================================================================


class RealityValidationRecommendation(Enum):
    """
    Recommendations after reality validation.
    
    CONFIRMED: Knowledge is supported by current perception
    WEAKENED: Some support exists but evidence is limited
    CONTRADICTED: Current perception contradicts the belief
    INSUFFICIENT_EVIDENCE: Not enough information to assess
    UNKNOWN: Validation outcome indeterminate
    """
    
    CONFIRMED = "confirmed"
    WEAKENED = "weakened"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNKNOWN = "unknown"


# =============================================================================
# REALITY VALIDATION REQUEST - Request to validate a belief
# =============================================================================


@dataclass(frozen=True)
class RealityValidationRequest:
    """
    Request to validate an existing knowledge artifact against current perception.
    
    Fields:
        request_identity:      Unique identifier
        
        knowledge_artifact:    Reference to the knowledge artifact to validate
        
        validation_scope:      What aspects need validation?
        
        expected_observations: What observations are expected if this is true?
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    request_identity: str
    
    # Knowledge reference (required)
    knowledge_artifact: str        # Reference to artifact being validated
    
    # Validation scope (required)
    validation_scope: str          # e.g., "temporal_extent", "semantic_content"
    
    # Expected observations
    expected_observations: Tuple[str, ...] = field(default_factory=tuple)  # Description of expected evidence
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate reality validation request."""
        if not self.request_identity:
            raise ValueError("request_identity is required")
    
    @classmethod
    def create(
        cls,
        knowledge_artifact_ref: str,
        validation_scope: str = "temporal_extent",
        expected_observations: Optional[List[str]] = None,
    ) -> "RealityValidationRequest":
        """Create a new reality validation request."""
        return cls(
            request_identity=f"reality_validation_request:{uuid.uuid4().hex[:24]}",
            knowledge_artifact=knowledge_artifact_ref,
            validation_scope=validation_scope,
            expected_observations=tuple(expected_observations or []),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_identity": self.request_identity,
            "knowledge_artifact": self.knowledge_artifact,
            "validation_scope": self.validation_scope,
            "expected_observations_count": len(self.expected_observations),
        }


# =============================================================================
# REALITY VALIDATION RESULT - Result of validation
# =============================================================================


@dataclass(frozen=True)
class RealityValidationResult:
    """
    Result of reality validation against current perception.
    
    Fields:
        result_identity:       Unique identifier
        
        request_reference:     Reference to the original request
        
        observed_support:      Observations that support the belief
        observed_contradiction: Observations that contradict the belief
        
        unresolved_observations: Observations that don't clearly support or contradict
        
        recommendation:        What should be done with this knowledge?
        
        confidence:            Confidence in validation result (0.0-1.0)
        uncertainty:           Uncertainty about this result
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    result_identity: str
    
    # Request reference (required)
    request_reference: str         # Reference to the original request
    
    # Recommendation (required) - before defaults
    recommendation: RealityValidationRecommendation  # What to do?
    
    # Evidence
    observed_support: Tuple[str, ...] = field(default_factory=tuple)  # Supporting observation IDs
    observed_contradiction: Tuple[str, ...] = field(default_factory=tuple)  # Contradicting obs ID
    unresolved_observations: Tuple[str, ...] = field(default_factory=tuple)  # Ambiguous observations
    
    confidence: float = 1.0        # Result confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about result
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate reality validation result."""
        if not self.result_identity:
            raise ValueError("result_identity is required")
    
    @property
    def net_evidence_ratio(self) -> float:
        """
        Calculate the ratio of supporting to contradicting evidence.
        
        Returns:
            Positive = net support, Negative = net contradiction
        """
        support = len(self.observed_support)
        contradict = len(self.observed_contradiction)
        total = support + contradict
        if total == 0:
            return 0.0
        return (support - contradict) / total
    
    @property
    def needs_revision(self) -> bool:
        """Check if this validation suggests the knowledge should be revised."""
        return self.recommendation in (
            RealityValidationRecommendation.WEAKENED,
            RealityValidationRecommendation.CONTRADICTED,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "result_identity": self.result_identity,
            "request_reference": self.request_reference,
            "observed_support_count": len(self.observed_support),
            "observed_contradiction_count": len(self.observed_contradiction),
            "unresolved_observations_count": len(self.unresolved_observations),
            "recommendation": self.recommendation.value,
            "confidence": self.confidence,
        }


# =============================================================================
# REALITY VALIDATION ENGINE - High-level validation results
# =============================================================================


@dataclass(frozen=True)
class RealityValidationEngineResult:
    """
    Result from the reality validation engine.
    
    Fields:
        result_identity:       Unique identifier
        
        validation_request:    The original request
        validation_result:     Detailed validation result
        
        confidence_distribution: Distribution of confidence scores across assessments
        
        overall_recommendation: Aggregate recommendation
        processing_time_sec:   Time taken for validation (optional)
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    result_identity: str
    
    # Request and result references (required)
    validation_request: RealityValidationRequest  # Original request
    validation_result: RealityValidationResult    # Detailed result
    
    # Processing stats
    confidence_distribution: Dict[str, float] = field(default_factory=dict)  # confidence_level -> count
    
    overall_recommendation: RealityValidationRecommendation = RealityValidationRecommendation.UNKNOWN
    processing_time_sec: Optional[float] = None  # Processing duration in seconds
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert engine result to dictionary."""
        return {
            "result_identity": self.result_identity,
            "validation_request": self.validation_request.to_dict(),
            "validation_result": self.validation_result.to_dict(),
            "confidence_distribution": dict(self.confidence_distribution),
            "overall_recommendation": self.overall_recommendation.value,
            "processing_time_sec": self.processing_time_sec,
        }


__all__ = [
    "ActivePerceptionOutcome",
    "ActivePerceptionRequest",
    "ActivePerceptionResponse",
    "RealityValidationRecommendation",
    "RealityValidationRequest",
    "RealityValidationResult",
    "RealityValidationEngineResult",
]