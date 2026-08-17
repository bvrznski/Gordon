# Perception Interface Response - Phase 5.2.5
# ============================================

"""
Perception Interface Response: Transport mechanism for interface responses.

Every response crossing the interface boundary shall:
- Reference its originating Request
- Expose one explicit status
- Preserve limitations, confidence, uncertainty and diagnostics where relevant
- Preserve publication and contract revision context
- Remain distinguishable (SUCCESS, PARTIAL, EMPTY, RESTRICTED, FAILED)
- Remain immutable after publication

RESPONSE-LAW-001: Every Interface Response shall reference its originating Request.
RESPONSE-LAW-002: Every Response shall expose one explicit status.
RESPONSE-LAW-003: Every Response shall preserve limitations, confidence, uncertainty and diagnostics where relevant.
RESPONSE-LAW-004: Every Response shall preserve publication and contract revision context.
RESPONSE-LAW-005: Partial, Empty, Restricted and Failed Responses shall remain distinguishable.
RESPONSE-LAW-006: Responses shall remain immutable after publication.
RESPONSE-LAW-007: Responses shall not expose hidden Perception internals.
RESPONSE-LAW-008: Response generation shall remain deterministic.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
import uuid


# =============================================================================
# RESPONSE STATUSES
# =============================================================================


class ResponseStatus:
    """Response status codes."""
    
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    EMPTY = "EMPTY"
    RESTRICTED = "RESTRICTED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


# =============================================================================
# INTERFACE RESPONSE
# =============================================================================


@dataclass(frozen=True)
class PerceptionInterfaceResponse:
    """
    Response from an Interface.
    
    Every response crossing the interface boundary shall have:
        - A reference to the originating request (request_reference)
        - An explicit status (status)
        - Limitations, confidence, uncertainty and diagnostics where relevant
        - Publication and contract revision context
        
    RESPONSE-LAW-001: Every Interface Response shall reference its originating Request.
    RESPONSE-LAW-002: Every Response shall expose one explicit status.
    RESPONSE-LAW-003: Every Response shall preserve limitations, confidence, uncertainty and diagnostics where relevant.
    RESPONSE-LAW-004: Every Response shall preserve publication and contract revision context.
    RESPONSE-LAW-005: Partial, Empty, Restricted and Failed Responses shall remain distinguishable.
    RESPONSE-LAW-006: Responses shall remain immutable after publication.
    RESPONSE-LAW-007: Responses shall not expose hidden Perception internals.
    RESPONSE-LAW-008: Response generation shall remain deterministic.
    """
    
    # Identity
    response_identity: str
    
    # Reference to originating request
    request_reference: str
    
    # Status (must be one of ResponseStatus)
    status: str  # SUCCESS, PARTIAL, EMPTY, RESTRICTED, FAILED, UNKNOWN
    
    # Payload (may be None for some statuses)
    payload: Optional[Any] = None
    
    # Limitations that applied
    limitations: Set[str] = field(default_factory=set)
    
    # Confidence in the result (0.0-1.0)
    confidence: float = 0.0
    
    # Uncertainty about the result (0.0-1.0)
    uncertainty: float = 1.0
    
    # Diagnostics information
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Publication context
    publication_revision: int = 1
    contract_revision: int = 1
    
    @classmethod
    def create_success(
        cls,
        request_ref: str,
        payload: Any,
        confidence: float = 1.0,
        **kwargs
    ) -> "PerceptionInterfaceResponse":
        """Create a success response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            status=ResponseStatus.SUCCESS,
            payload=payload,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            publication_revision=kwargs.get("publication_revision", 1),
            contract_revision=kwargs.get("contract_revision", 1),
        )
    
    @classmethod
    def create_partial(
        cls,
        request_ref: str,
        payload: Any,
        limitations: List[str],
        confidence: float = 0.5,
        **kwargs
    ) -> "PerceptionInterfaceResponse":
        """Create a partial success response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            status=ResponseStatus.PARTIAL,
            payload=payload,
            limitations=set(limitations),
            confidence=confidence,
            uncertainty=1.0 - confidence,
            publication_revision=kwargs.get("publication_revision", 1),
            contract_revision=kwargs.get("contract_revision", 1),
        )
    
    @classmethod
    def create_empty(
        cls,
        request_ref: str,
        **kwargs
    ) -> "PerceptionInterfaceResponse":
        """Create an empty response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            status=ResponseStatus.EMPTY,
            payload=None,
            publication_revision=kwargs.get("publication_revision", 1),
            contract_revision=kwargs.get("contract_revision", 1),
        )
    
    @classmethod
    def create_restricted(
        cls,
        request_ref: str,
        limitations: List[str],
        **kwargs
    ) -> "PerceptionInterfaceResponse":
        """Create a restricted response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            status=ResponseStatus.RESTRICTED,
            payload=None,
            limitations=set(limitations),
            publication_revision=kwargs.get("publication_revision", 1),
            contract_revision=kwargs.get("contract_revision", 1),
        )
    
    @classmethod
    def create_failed(
        cls,
        request_ref: str,
        error_message: str,
        failure_kind: str = "unknown",
        **kwargs
    ) -> "PerceptionInterfaceResponse":
        """Create a failed response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            status=ResponseStatus.FAILED,
            payload=None,
            limitations={"error", failure_kind},
            diagnostics={
                "error": error_message,
                "failure_kind": failure_kind,
                "timestamp": _time.time(),
            },
            publication_revision=kwargs.get("publication_revision", 1),
            contract_revision=kwargs.get("contract_revision", 1),
        )
    
    @classmethod
    def create_unknown(
        cls,
        request_ref: str,
        **kwargs
    ) -> "PerceptionInterfaceResponse":
        """Create an unknown status response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            status=ResponseStatus.UNKNOWN,
            payload=None,
            diagnostics={"reason": "status could not be determined"},
            publication_revision=kwargs.get("publication_revision", 1),
            contract_revision=kwargs.get("contract_revision", 1),
        )
    
    def is_success(self) -> bool:
        """Check if response indicates success."""
        return self.status == ResponseStatus.SUCCESS
    
    def is_error(self) -> bool:
        """Check if response indicates an error state."""
        return self.status in (ResponseStatus.FAILED, ResponseStatus.UNKNOWN)
    
    def has_limitations(self) -> bool:
        """Check if limitations were applied."""
        return len(self.limitations) > 0
    
    @property
    def is_valid(self) -> bool:
        """Validate response data."""
        valid_statuses = {
            ResponseStatus.SUCCESS,
            ResponseStatus.PARTIAL,
            ResponseStatus.EMPTY,
            ResponseStatus.RESTRICTED,
            ResponseStatus.FAILED,
            ResponseStatus.UNKNOWN,
        }
        
        if self.status not in valid_statuses:
            return False
        
        if self.confidence < 0.0 or self.confidence > 1.0:
            return False
        
        if self.uncertainty < 0.0 or self.uncertainty > 1.0:
            return False
        
        if abs(self.confidence + self.uncertainty - 1.0) > 0.01 and self.payload is not None:
            # Confidence + uncertainty should approximately sum to 1 for non-empty responses
            pass  # Not necessarily invalid
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "response_identity": self.response_identity,
            "request_reference": self.request_reference,
            "status": self.status,
            "payload": self.payload,
            "limitations": list(self.limitations),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "diagnostics": dict(self.diagnostics),
            "publication_revision": self.publication_revision,
            "contract_revision": self.contract_revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionInterfaceResponse":
        """Create response from dictionary."""
        return cls(
            response_identity=data.get("response_identity", ""),
            request_reference=data.get("request_reference", ""),
            status=data.get("status", ResponseStatus.UNKNOWN),
            payload=data.get("payload"),
            limitations=set(data.get("limitations", [])),
            confidence=float(data.get("confidence", 0.0)),
            uncertainty=float(data.get("uncertainty", 1.0)),
            diagnostics=dict(data.get("diagnostics", {})),
            publication_revision=int(data.get("publication_revision", 1)),
            contract_revision=int(data.get("contract_revision", 1)),
        )


# =============================================================================
# SENSOR ACQUISITION RESPONSE
# =============================================================================


@dataclass(frozen=True)
class SensorAcquisitionResponse:
    """
    Response to a sensor acquisition request.
    
    Fields:
        acquisition_session: Unique identifier for this acquisition session
        effective_capabilities: What was actually available during acquisition
        effective_sampling_config: Sampling configuration that was used
        effective_permission_scope: Permissions that were granted
        effective_sandbox_scope: Sandbox restrictions that applied
        calibration_state: Calibration status of the sensor
        limitations: Any constraints that limited the acquisition
        status: Overall acquisition status
    """
    
    request_reference: str
    
    # Acquisition session
    acquisition_session: str = field(default_factory=lambda: f"session:{uuid.uuid4().hex[:16]}")
    
    # Effective capabilities (may differ from requested)
    effective_capabilities: Dict[str, Any] = field(default_factory=dict)
    
    # Effective sampling configuration
    effective_sampling_config: Dict[str, Any] = field(default_factory=dict)
    
    # Permission and sandbox scope
    effective_permission_scope: Dict[str, Any] = field(default_factory=dict)
    effective_sandbox_scope: Dict[str, Any] = field(default_factory=dict)
    
    # Calibration state
    calibration_state: str = "unknown"
    calibration_reference: Optional[str] = None
    
    # Limitations that applied
    limitations: Set[str] = field(default_factory=set)
    
    # Status (SUCCESS, PARTIAL, FAILED, etc.)
    status: str = ResponseStatus.SUCCESS
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_success(
        cls,
        request_ref: str,
        capabilities: Dict[str, Any],
        sampling_config: Dict[str, Any],
        calibration_state: str = "calibrated",
        **kwargs
    ) -> "SensorAcquisitionResponse":
        """Create a successful acquisition response."""
        return cls(
            request_reference=request_ref,
            effective_capabilities=dict(capabilities),
            effective_sampling_config=dict(sampling_config),
            calibration_state=calibration_state,
            calibration_reference=kwargs.get("calibration_reference"),
            status=ResponseStatus.SUCCESS,
        )
    
    @classmethod
    def create_partial(
        cls,
        request_ref: str,
        capabilities: Dict[str, Any],
        limitations: List[str],
        **kwargs
    ) -> "SensorAcquisitionResponse":
        """Create a partial acquisition response."""
        return cls(
            request_reference=request_ref,
            effective_capabilities=dict(capabilities),
            limitations=set(limitations),
            status=ResponseStatus.PARTIAL,
        )
    
    @classmethod
    def create_failed(
        cls,
        request_ref: str,
        failure_kind: str,
        **kwargs
    ) -> "SensorAcquisitionResponse":
        """Create a failed acquisition response."""
        return cls(
            request_reference=request_ref,
            status=ResponseStatus.FAILED,
            diagnostics={
                "failure_kind": failure_kind,
                "timestamp": _time.time(),
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request_reference": self.request_reference,
            "acquisition_session": self.acquisition_session,
            "effective_capabilities": dict(self.effective_capabilities),
            "effective_sampling_config": dict(self.effective_sampling_config),
            "effective_permission_scope": dict(self.effective_permission_scope),
            "effective_sandbox_scope": dict(self.effective_sandbox_scope),
            "calibration_state": self.calibration_state,
            "calibration_reference": self.calibration_reference,
            "limitations": list(self.limitations),
            "status": self.status,
            "diagnostics": dict(self.diagnostics),
        }


# =============================================================================
# WORKSPACE PUBLICATION RESPONSE
# =============================================================================


@dataclass(frozen=True)
class PerceptionWorkspacePublication:
    """
    Workspace-compatible publication from Perception.
    
    Fields:
        publication_identity: Unique identifier for this publication
        request_reference: Reference to the originating request (if any)
        candidate_workspace_projection: The proposed workspace projection
        source_revisions: revisions of source artifacts
        representation_size: Size in bytes of the representation
        freshness: How recent the data is (0.0-1.0)
        conflicts: List of detected conflicts
        ambiguities: List of detected ambiguities
        missing_evidence: List of missing evidence items
        limitations: Any constraints that applied
    """
    
    publication_identity: str = field(default_factory=lambda: f"pub:{uuid.uuid4().hex[:16]}")
    
    request_reference: Optional[str] = None
    
    candidate_workspace_projection: Dict[str, Any] = field(default_factory=dict)
    
    source_revisions: Dict[str, int] = field(default_factory=dict)
    
    representation_size: int = 0
    freshness: float = 1.0
    
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    ambiguities: List[Dict[str, Any]] = field(default_factory=list)
    missing_evidence: List[Dict[str, Any]] = field(default_factory=list)
    
    limitations: Set[str] = field(default_factory=set)
    
    @classmethod
    def create(
        cls,
        projection: Dict[str, Any],
        source_revisions: Optional[Dict[str, int]] = None,
        **kwargs
    ) -> "PerceptionWorkspacePublication":
        """Create a workspace publication."""
        return cls(
            candidate_workspace_projection=dict(projection),
            source_revisions=source_revisions or {},
            representation_size=kwargs.get("representation_size", 0),
            freshness=kwargs.get("freshness", 1.0),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "publication_identity": self.publication_identity,
            "request_reference": self.request_reference,
            "candidate_workspace_projection": dict(self.candidate_workspace_projection),
            "source_revisions": dict(self.source_revisions),
            "representation_size": self.representation_size,
            "freshness": self.freshness,
            "conflicts": list(self.conflicts),
            "ambiguities": list(self.ambiguities),
            "missing_evidence": list(self.missing_evidence),
            "limitations": list(self.limitations),
        }


# =============================================================================
# WORKSPACE FEEDBACK
# =============================================================================


@dataclass(frozen=True)
class WorkspacePerceptionFeedback:
    """
    Feedback from Workspace about a Perception publication.
    
    Fields:
        publication_reference: Reference to the published artifact
        admission_outcome: What Workspace decided (admit, reject, defer, etc.)
        admitted_components: Which components were accepted
        rejected_components: Which components were rejected and why
        rejection_reasons: Detailed reasons for rejections
        representation_constraints: Any constraints applied to representation
        requested_revision: Revision number if updated
    """
    
    publication_reference: str
    
    admission_outcome: str  # ADMITTED, REJECTED, DEFERRED, ESCALATED
    
    admitted_components: List[Dict[str, Any]] = field(default_factory=list)
    rejected_components: List[Dict[str, Any]] = field(default_factory=list)
    
    rejection_reasons: List[str] = field(default_factory=list)
    representation_constraints: Dict[str, Any] = field(default_factory=dict)
    
    requested_revision: int = 1
    
    @classmethod
    def create_admitted(
        cls,
        pub_ref: str,
        admitted_components: List[Dict[str, Any]],
        **kwargs
    ) -> "WorkspacePerceptionFeedback":
        """Create feedback for an admitted publication."""
        return cls(
            publication_reference=pub_ref,
            admission_outcome="ADMITTED",
            admitted_components=list(admitted_components),
        )
    
    @classmethod
    def create_rejected(
        cls,
        pub_ref: str,
        rejection_reasons: List[str],
        **kwargs
    ) -> "WorkspacePerceptionFeedback":
        """Create feedback for a rejected publication."""
        return cls(
            publication_reference=pub_ref,
            admission_outcome="REJECTED",
            rejection_reasons=list(rejection_reasons),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "publication_reference": self.publication_reference,
            "admission_outcome": self.admission_outcome,
            "admitted_components": list(self.admitted_components),
            "rejected_components": list(self.rejected_components),
            "rejection_reasons": list(self.rejection_reasons),
            "representation_constraints": dict(self.representation_constraints),
            "requested_revision": self.requested_revision,
        }


# =============================================================================
# MEMORY SUBMISSION RESPONSE
# =============================================================================


@dataclass(frozen=True)
class PerceptionMemoryAdmissionResponse:
    """
    Response to a memory candidate submission.
    
    Fields:
        submission_reference: Reference to the original submission
        outcome: The admission decision (ADMITTED, PARTIALLY_ADMITTED, REJECTED, etc.)
        admitted_candidates: List of admitted artifact references
        rejected_candidates: List of rejected candidates with reasons
        deferred_candidates: List of candidates deferred for later evaluation
        admission_conditions: Any conditions on admission
        memory_artifact_references: Memory-assigned identifiers (if admitted)
    """
    
    submission_reference: str
    
    outcome: str  # ADMITTED, PARTIALLY_ADMITTED, REJECTED, DEFERRED, ESCALATED, FAILED, UNKNOWN
    
    admitted_candidates: List[Dict[str, Any]] = field(default_factory=list)
    rejected_candidates: List[Dict[str, Any]] = field(default_factory=list)
    deferred_candidates: List[Dict[str, Any]] = field(default_factory=list)
    
    admission_conditions: Dict[str, Any] = field(default_factory=dict)
    memory_artifact_references: List[str] = field(default_factory=list)
    
    @classmethod
    def create_admitted(
        cls,
        submission_ref: str,
        admitted_candidates: List[Dict[str, Any]],
        **kwargs
    ) -> "PerceptionMemoryAdmissionResponse":
        """Create response for admitted candidates."""
        return cls(
            submission_reference=submission_ref,
            outcome="ADMITTED",
            admitted_candidates=list(admitted_candidates),
        )
    
    @classmethod
    def create_partially_admitted(
        cls,
        submission_ref: str,
        admitted: List[Dict[str, Any]],
        rejected: List[Dict[str, Any]],
        **kwargs
    ) -> "PerceptionMemoryAdmissionResponse":
        """Create response for partially admitted candidates."""
        return cls(
            submission_reference=submission_ref,
            outcome="PARTIALLY_ADMITTED",
            admitted_candidates=list(admitted),
            rejected_candidates=list(rejected),
        )
    
    @classmethod
    def create_rejected(
        cls,
        submission_ref: str,
        rejection_reasons: List[str],
        **kwargs
    ) -> "PerceptionMemoryAdmissionResponse":
        """Create response for rejected candidates."""
        return cls(
            submission_reference=submission_ref,
            outcome="REJECTED",
            rejected_candidates=[{"reason": r} for r in rejection_reasons],
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "submission_reference": self.submission_reference,
            "outcome": self.outcome,
            "admitted_candidates": list(self.admitted_candidates),
            "rejected_candidates": list(self.rejected_candidates),
            "deferred_candidates": list(self.deferred_candidates),
            "admission_conditions": dict(self.admission_conditions),
            "memory_artifact_references": list(self.memory_artifact_references),
        }


# =============================================================================
# GROUNDING RESPONSE (Knowledge, Identity)
# =============================================================================


@dataclass(frozen=True)
class PerceptionGroundingResponse:
    """
    Response to a grounding request.
    
    Fields:
        request_reference: Reference to the originating request
        concept_candidates: List of candidate concepts
        category_candidates: List of candidate categories
        schema_mappings: Mappings to known schemas
        expected_properties: Properties that were expected but missing
        incompatible_properties: Properties that conflict with concepts
        confidence: Overall confidence in grounding (0.0-1.0)
    """
    
    request_reference: str
    
    concept_candidates: List[Dict[str, Any]] = field(default_factory=list)
    category_candidates: List[Dict[str, Any]] = field(default_factory=list)
    
    schema_mappings: Dict[str, Any] = field(default_factory=dict)
    
    expected_properties: List[str] = field(default_factory=list)
    incompatible_properties: List[str] = field(default_factory=list)
    
    confidence: float = 0.0
    uncertainty: float = 1.0
    
    @classmethod
    def create(
        cls,
        request_ref: str,
        concept_candidates: Optional[List[Dict[str, Any]]] = None,
        category_candidates: Optional[List[Dict[str, Any]]] = None,
        confidence: float = 1.0,
        **kwargs
    ) -> "PerceptionGroundingResponse":
        """Create a grounding response."""
        return cls(
            request_reference=request_ref,
            concept_candidates=list(concept_candidates or []),
            category_candidates=list(category_candidates or []),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request_reference": self.request_reference,
            "concept_candidates": list(self.concept_candidates),
            "category_candidates": list(self.category_candidates),
            "schema_mappings": dict(self.schema_mappings),
            "expected_properties": list(self.expected_properties),
            "incompatible_properties": list(self.incompatible_properties),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


__all__ = [
    # Status codes
    "ResponseStatus",
    
    # Core response types
    "PerceptionInterfaceResponse",
    
    # Sensor responses
    "SensorAcquisitionResponse",
    
    # Workspace responses
    "PerceptionWorkspacePublication",
    "WorkspacePerceptionFeedback",
    
    # Memory responses  
    "PerceptionMemoryAdmissionResponse",
    
    # Grounding responses
    "PerceptionGroundingResponse",
]