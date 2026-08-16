# Perception Processing Request - Phase 5.2.2
# ============================================

"""
Processing Request: Specification for what transformation to perform.

A ProcessingRequest describes the desired transformation without being
an artifact itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PROCESSING REQUEST - What transformation is requested?
# =============================================================================


@dataclass(frozen=True)
class PerceptionProcessingRequest:
    """
    Request for perception processing.
    
    Fields:
        request_identity:     Unique request identifier
        source_artifacts:     Artifacts to be processed (references only)
        requested_pipeline:   Pipeline ID to use, or transformation outcome
        processing_context:   Context for the processing
        modality_descriptor:  Which modality produces these artifacts?
        calibration_reference: Reference to calibration data
        permission_context:   Permission context for processing
        sandbox_context:      Sandbox environment context
        configuration_reference: Configuration version to use
        constraints:          Processing constraints (timeout, resource limits)
    """
    
    request_identity: str                  # Unique ID
    
    source_artifacts: Tuple[str, ...]      # Artifact IDs to process
    
    requested_pipeline: Optional[str] = None  # Pipeline ID or transformation goal
    
    processing_context: Dict[str, Any] = field(default_factory=dict)  # Context data
    modality_descriptor: str = "unknown"   # e.g., "console", "vision"
    
    calibration_reference: Optional[str] = None  # Calibration version ref
    permission_context: Tuple[str, ...] = field(default_factory=tuple)
    sandbox_context: Tuple[str, ...] = field(default_factory=tuple)
    
    configuration_reference: Optional[int] = None  # Config revision
    
    constraints: Dict[str, Any] = field(default_factory=dict)  # timeout, resources, etc.
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Request origin
    
    @property
    def is_valid(self) -> bool:
        """Check if request has minimal required data."""
        return (
            len(self.request_identity) > 0 and
            len(self.source_artifacts) > 0
        )
    
    @classmethod
    def create(
        cls,
        source_artifact_ids: List[str],
        requested_pipeline: Optional[str] = None,
        modality_descriptor: str = "unknown",
        calibration_ref: Optional[str] = None,
        permission_context: Optional[List[str]] = None,
        sandbox_context: Optional[List[str]] = None,
        config_ref: Optional[int] = None,
    ) -> "PerceptionProcessingRequest":
        """
        Create a new processing request.
        
        Args:
            source_artifact_ids: IDs of artifacts to process
            requested_pipeline: Pipeline ID or transformation outcome (optional)
            modality_descriptor: Source modality
            calibration_ref: Calibration version reference (optional)
            permission_context: Permission set (optional)
            sandbox_context: Sandbox context (optional)
            config_ref: Configuration revision (optional)
            
        Returns:
            New PerceptionProcessingRequest
        """
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            source_artifacts=tuple(source_artifact_ids),
            requested_pipeline=requested_pipeline,
            processing_context={},
            modality_descriptor=modality_descriptor,
            calibration_reference=calibration_ref,
            permission_context=tuple(permission_context or []),
            sandbox_context=tuple(sandbox_context or []),
            configuration_reference=config_ref,
            constraints={},
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_identity": self.request_identity,
            "source_artifacts": list(self.source_artifacts),
            "requested_pipeline": self.requested_pipeline,
            "processing_context": dict(self.processing_context),
            "modality_descriptor": self.modality_descriptor,
            "calibration_reference": self.calibration_reference,
            "permission_context": list(self.permission_context),
            "sandbox_context": list(self.sandbox_context),
            "configuration_reference": self.configuration_reference,
            "constraints": dict(self.constraints),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionProcessingRequest":
        """Create request from dictionary."""
        return cls(
            request_identity=data.get("request_identity", str(uuid.uuid4())),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            requested_pipeline=data.get("requested_pipeline"),
            processing_context=dict(data.get("processing_context", {})),
            modality_descriptor=data.get("modality_descriptor", "unknown"),
            calibration_reference=data.get("calibration_reference"),
            permission_context=tuple(data.get("permission_context", [])),
            sandbox_context=tuple(data.get("sandbox_context", [])),
            configuration_reference=data.get("configuration_reference"),
            constraints=dict(data.get("constraints", {})),
            provenance=dict(data.get("provenance", {})),
        )