# Partial Perception Integration - Phase 5.2.3
# ============================================

"""
Partial Integration: Integration that could not complete fully.

A PartialIntegration represents a valid result when some integration
components could not be completed due to missing artifacts or constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PARTIAL INTEGRATION STATE - Incomplete integration state
# =============================================================================


@dataclass(frozen=True)
class PartialPerceptionIntegration:
    """
    State of a partial integration operation.
    
    Fields:
        integration_identity: Unique identifier for this integration attempt
        request_reference: Reference to the original request
        participating_artifacts: Artifacts that were integrated
        missing_artifacts: Which artifacts were missing?
        unavailable_modalities: Which modalities couldn't provide data?
        completed_bindings: What bindings succeeded?
        unresolved_bindings: What bindings remain ambiguous?
        confidence_limit: Upper bound on achievable confidence
        uncertainty_increase: How much did uncertainty increase?
    """
    
    integration_identity: str              # Unique ID
    
    request_reference: str                 # Reference to original request
    
    participating_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Integrated
    missing_artifacts: Tuple[str, ...] = field(default_factory=tuple)        # Missing
    unavailable_modalities: Tuple[str, ...] = field(default_factory=tuple)   # Unavailable
    
    completed_bindings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    unresolved_bindings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    confidence_limit: float = 0.5          # Max achievable confidence
    uncertainty_increase: float = 0.3      # Increased from missing evidence
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        """Check if integration was complete."""
        return len(self.missing_artifacts) == 0 and len(self.unavailable_modalities) == 0
    
    @property
    def missing_count(self) -> int:
        """Number of missing artifacts."""
        return len(self.missing_artifacts)
    
    @property
    def modality_gap_count(self) -> int:
        """Number of unavailable modalities."""
        return len(self.unavailable_modalities)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert partial integration state to dictionary."""
        return {
            "integration_identity": self.integration_identity,
            "request_reference": self.request_reference,
            "participating_artifacts_count": len(self.participating_artifacts),
            "participating_artifacts": list(self.participating_artifacts),
            "missing_artifacts_count": len(self.missing_artifacts),
            "missing_artifacts": list(self.missing_artifacts),
            "unavailable_modalities_count": len(self.unavailable_modalities),
            "unavailable_modalities": list(self.unavailable_modalities),
            "completed_bindings_count": len(self.completed_bindings),
            "unresolved_bindings_count": len(self.unresolved_bindings),
            "confidence_limit": self.confidence_limit,
            "uncertainty_increase": self.uncertainty_increase,
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PartialPerceptionIntegration":
        """Create partial integration state from dictionary."""
        return cls(
            integration_identity=data.get("integration_identity", str(uuid.uuid4())),
            request_reference=data.get("request_reference", ""),
            participating_artifacts=tuple(data.get("participating_artifacts", [])),
            missing_artifacts=tuple(data.get("missing_artifacts", [])),
            unavailable_modalities=tuple(data.get("unavailable_modalities", [])),
        )


# =============================================================================
# MISSING EVIDENCE - What evidence is missing?
# =============================================================================


@dataclass(frozen=True)
class MissingPerceptualEvidence:
    """
    Record of expected but missing evidence.
    
    Fields:
        expected_source: Which artifact was expected?
        expected_modality: Which modality should provide it?
        expected_artifact_kind: What kind of artifact is expected?
        absence_reason: Why is it absent? (enum)
        observation_window: When was it expected?
        observability_assumption: What's assumed about observability
        negative_evidence_validity: Can we infer negation from absence?
    """
    
    expected_source: str                   # Expected artifact reference
    
    expected_modality: str                 # Expected modality
    expected_artifact_kind: str            # Expected artifact type
    
    absence_reason: str = "not_observed"   # See AbsenceReason enum
    observation_window: Dict[str, Any] = field(default_factory=dict)  # time range, etc.
    
    observability_assumption: str = "complete"  # Assuming full visibility?
    negative_evidence_validity: float = 0.0  # Can absence imply negation?
    
    confidence: float = 1.0
    uncertainty: float = 0.5
    
    provenance: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# INTEGRATION EVIDENCE REQUIREMENT - What additional evidence is needed?
# =============================================================================


@dataclass(frozen=True)
class IntegrationEvidenceRequirement:
    """
    Requirement for additional evidence to resolve integration ambiguity.
    
    Fields:
        requirement_identity: Unique identifier
        unresolved_question: What question remains unanswered?
        required_modality: Which modality is needed?
        required_artifact_kind: What kind of artifact is needed?
        required_temporal_scope: When should it be observed?
        required_spatial_scope: Where should it be observed?
        expected_discriminating_value: How will this help distinguish alternatives?
    """
    
    requirement_identity: str              # Unique ID
    
    unresolved_question: str               # What needs answering?
    
    required_modality: str                 # Needed modality
    required_artifact_kind: str            # Needed artifact type
    
    required_temporal_scope: Dict[str, Any] = field(default_factory=dict)
    required_spatial_scope: Dict[str, Any] = field(default_factory=dict)
    
    expected_discriminating_value: float = 0.5  # Expected impact (0.0-1.0)
    
    priority: str = "medium"               # low, medium, high
    provenance: Dict[str, Any] = field(default_factory=dict)