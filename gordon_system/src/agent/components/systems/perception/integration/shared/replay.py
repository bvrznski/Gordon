# Integration Replay - Phase 5.2.3
# =================================

"""
Integration Replay: Reproduce integration with the same context.

Replay enables deterministic verification and debugging of integration results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# INTEGRATION REPLAY - Replay integration with preserved context
# =============================================================================


@dataclass(frozen=True)
class PerceptionIntegrationReplay:
    """
    Replay of a previous integration operation.
    
    Fields:
        replay_identity: Unique identifier for this replay
        original_result: Reference to the original result being replayed
        source_artifact_revisions: Revisions of source artifacts during replay
        processing_revisions: Processing pipeline revisions
        correspondence_revisions: Correspondence rule revisions
        binding_policy_revisions: Binding policy revisions
        fusion_strategy_revisions: Fusion strategy revisions
        confidence_policy_revisions: Confidence policy revisions
        uncertainty_policy_revisions: Uncertainty policy revisions
        permission_context: Permission context during replay
        sandbox_context: Sandbox context during replay
        
        replay_result: Result from the replay operation
        mismatch_report: Differences between original and replay results
    """
    
    replay_identity: str                   # Unique ID
    
    original_result: Dict[str, Any]        # Reference to original result
    
    source_artifact_revisions: Dict[str, int] = field(default_factory=dict)
    processing_revisions: Dict[str, int] = field(default_factory=dict)
    
    correspondence_revisions: Dict[str, int] = field(default_factory=dict)
    binding_policy_revisions: Dict[str, int] = field(default_factory=dict)
    fusion_strategy_revisions: Dict[str, int] = field(default_factory=dict)
    
    confidence_policy_revisions: Dict[str, int] = field(default_factory=dict)
    uncertainty_policy_revisions: Dict[str, int] = field(default_factory=dict)
    
    permission_context: Tuple[str, ...] = field(default_factory=tuple)
    sandbox_context: Tuple[str, ...] = field(default_factory=tuple)
    
    replay_result: Optional[Dict[str, Any]] = None  # Result from replay
    mismatch_report: Dict[str, Any] = field(default_factory=dict)  # Differences
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_deterministic(self) -> bool:
        """Check if replay produced identical results."""
        return len(self.mismatch_report) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert replay to dictionary."""
        return {
            "replay_identity": self.replay_identity,
            "original_result_ref": self.original_result.get("request_reference", ""),
            "source_artifact_revisions_count": len(self.source_artifact_revisions),
            "processing_revisions_count": len(self.processing_revisions),
            "correspondence_revisions_count": len(self.correspondence_revisions),
            "binding_policy_revisions_count": len(self.binding_policy_revisions),
            "fusion_strategy_revisions_count": len(self.fusion_strategy_revisions),
            "confidence_policy_revisions_count": len(self.confidence_policy_revisions),
            "uncertainty_policy_revisions_count": len(self.uncertainty_policy_revisions),
            "permission_context_count": len(self.permission_context),
            "sandbox_context_count": len(self.sandbox_context),
            "replay_result_available": self.replay_result is not None,
            "mismatch_report_count": len(self.mismatch_report),
            "is_deterministic": self.is_deterministic,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def create(
        cls,
        original_result: Dict[str, Any],
        context_overrides: Optional[Dict[str, Any]] = None,
    ) -> "PerceptionIntegrationReplay":
        """Create a replay request."""
        return cls(
            replay_identity=f"replay:{uuid.uuid4().hex[:16]}",
            original_result=original_result,
            permission_context=context_overrides.get("permission_context", ()) if context_overrides else (),
            sandbox_context=context_overrides.get("sandbox_context", ()) if context_overrides else (),
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "context_override_count": len(context_overrides or {}),
            },
        )


# =============================================================================
# INTEGRATION VALIDATION - Validate integration results
# =============================================================================


@dataclass(frozen=True)
class PerceptionIntegrationValidation:
    """
    Validation result for an integration operation.
    
    Fields:
        validation_identity: Unique identifier
        request_reference: Reference to the validated request
        source_artifact_validity: Are sources valid?
        processing_validity: Was processing complete?
        ontology_validity: Does output match expected ontology?
        dependency_analysis_validity: Was dependency analysis correct?
        correspondence_consistency: Are correspondences consistent?
        binding_consistency: Are bindings consistent?
        fusion_compatibility: Is fusion compatible with evidence?
    """
    
    validation_identity: str               # Unique ID
    
    request_reference: str                 # Reference to validated request
    
    source_artifact_validity: bool = True
    processing_validity: bool = True
    ontology_validity: bool = True
    
    dependency_analysis_validity: bool = True
    correspondence_consistency: bool = True
    binding_consistency: bool = True
    fusion_compatibility: bool = True
    
    validation_failures: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence: float = 1.0                # Confidence in validity
    uncertainty: float = 0.0               # Known limitations of validity
    
    provenance: Dict[str, Any] = field(default_factory=dict)